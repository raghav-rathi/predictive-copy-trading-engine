#!/usr/bin/env python3
"""Paper-first runner for the Hyperliquid copy engine.

This is the default and intended mode: it replays an NDJSON fill stream
through the same decision path live trading would use (targets ->
clustering -> intent aggregation -> risk -> sizing -> mirror -> exits
-> reconcile), opens hypothetical positions, and logs everything:

  * data/hyperliquid_paper_trades.csv — closed trades with PnL (the
    track record the live gate reads);
  * data/hyperliquid_decisions.ndjson — every open/skip/close with the
    reason (score, Kelly edge, cluster vote, risk);
  * data/hyperliquid_shadow.csv — shadow positions: skipped signals
    priced at marks so the strategy stays improvable. A skip that would
    have printed money is how the thresholds get better.

THE PAPER-TRADE GATE: with hyperliquid.live_trading=true, paper.py
refuses to proceed (exit code 4) unless the CSV already holds at least
paper.gate.min_closed_trades closed trades with aggregate PnL >=
paper.gate.min_total_pnl_usd. Live execution is NOT wired even then
(mirror.LiveExecutor raises by design) — the gate is necessary, not
sufficient.

Event types (one JSON object per line):
  {"type":"fill","user":"0x..","coin":"BTC","dir":"Open Long",
   "sz":1.0,"px":95000.0,"startPosition":0.0,"ts":...,"hash":"..."}
  {"type":"mark","coin":"BTC","px":95100.0,"ts":...}
  {"type":"tick","ts":...}   (drives intent flushes, exits, reconcile)
  {"type":"target_positions","user":"0x..",
   "positions":[{"coin":"BTC","size":1.5}],"ts":...}
   (startup sync: paper equivalent of reconcile.fetch_all_target_positions)

Fill fragmentation: a leader's entry arrives as many small fills. The
IntentAggregator groups (user, coin, dir) fills inside
mirror.intent_window_s into one intent (total size, size-weighted px)
and dedupes by fill hash, so the engine copies once per intent and
replays never double-copy.

Usage:
  python3 hyperliquid/paper.py --config hyperliquid/config.example.json \
      --fills hyperliquid/examples/sample_fills.ndjson \
      --targets hyperliquid/examples/targets.sample.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config
from costs import FundingLedger, round_trip_costs, taker_fee_rate
from targets import load_targets, cluster_wallets, cluster_vote
from mirror import decide_fill, TargetBook, IntentAggregator, EPS
from sizing import size_copy, kelly_fstar
from exits import ExitManager, synced_close_size
from reconcile import check_drift
from risk import Risk
from notify import build_notifier

PAPER_FIELDS = ["trade_id", "mode", "target", "coin", "side", "entry_ts",
                "entry_px", "size", "exit_ts", "exit_px", "exit_reason",
                "pnl_usd", "pnl_pct", "fees_usd", "funding_usd"]
SHADOW_FIELDS = ["shadow_id", "target", "coin", "side", "entry_ts",
                 "entry_px", "size", "exit_ts", "exit_px", "exit_reason",
                 "pnl_usd", "skip_reason", "fees_usd", "funding_usd"]


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[paper {ts}] {msg}", file=sys.stderr, flush=True)


def loud(msg: str) -> None:
    bar = "!" * 72
    print(f"\n{bar}\n{msg}\n{bar}\n", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------
# Paper ledger
# --------------------------------------------------------------------------

class Paper:
    def __init__(self, cfg: dict, targets: dict, clusters: list[set]):
        h = cfg["hyperliquid"]
        self.cfg = cfg
        self.targets = targets
        self.clusters = clusters
        self.votes = self._build_votes()
        self.book = TargetBook()
        self.intents = IntentAggregator(h["mirror"]["intent_window_s"])
        self.notifier = build_notifier(cfg)
        self.positions: dict[tuple[str, str], dict] = {}
        self.marks: dict[str, float] = {}
        self.shadows: dict[int, dict] = {}
        self.risk = Risk(h["risk"], h["mirror"]["coin_whitelist"],
                         notify=self.notifier.emit)
        self.exits = ExitManager(h["exits"]["stop_loss_pct"],
                                 h["exits"]["take_profit_pct"],
                                 h["exits"]["max_hold_seconds"],
                                 h["exits"]["trailing_stop_pct"],
                                 h["exits"]["max_position_age_seconds"])
        self.next_id = 1
        self.next_shadow = 1
        self.last_reconcile = 0.0
        # Honest cost accounting (STRATEGY_RESEARCH.md 4a+5): taker fees
        # on both legs of every close, and hourly funding accrual over
        # the hold. Config is optional — defaults are the documented
        # base fee schedule and funding on.
        cc = h.get("costs", {}) or {}
        self.taker_fee, fee_src = taker_fee_rate(
            h.get("info_url", "https://api.hyperliquid.xyz/info"),
            cc.get("account"))
        self.funding = FundingLedger(
            h.get("info_url", "https://api.hyperliquid.xyz/info")) \
            if cc.get("funding_accounting", True) else None
        log(f"cost accounting: taker fee {self.taker_fee:.5%} ({fee_src}); "
            f"funding {'on' if self.funding else 'off'}")
        p = h["paper"]
        self.csv_path = p["paper_trades_csv"]
        self.dec_path = p["decision_log"]
        self.shadow_path = p["shadow_csv"]
        for path in (self.csv_path, self.dec_path, self.shadow_path):
            d = os.path.dirname(path)
            if d:
                os.makedirs(d, exist_ok=True)

    def _build_votes(self) -> dict[str, dict]:
        votes: dict[str, dict] = {}
        thr = self.cfg["hyperliquid"]["scorer"]["mirror_score_threshold"]
        for cl in self.clusters:
            v = cluster_vote(cl, self.targets, thr)
            for u in cl:
                votes[u] = v
        return votes

    # -- logging ---------------------------------------------------------

    def decide(self, entry: dict) -> None:
        entry = {"ts": entry.get("ts"), **entry}
        with open(self.dec_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _append(self, path: str, fields: list, row: dict, write_header: bool):
        new = write_header and not os.path.exists(path)
        with open(path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            if new:
                w.writeheader()
            w.writerow(row)

    # -- fills -----------------------------------------------------------

    def _target_closes(self, user: str) -> list[float]:
        """Rolling realized closes for the target (paper: from our mirror
        of their fills is not their PnL — use scored stats when present)."""
        stats = (self.targets.get(user) or {}).get("stats") or {}
        return list(stats.get("recent_closes_usd") or [])

    def on_fill(self, fill: dict) -> None:
        ts = float(fill.get("time", fill.get("ts", 0)) or 0)
        dup, rolled = self.intents.add(fill)
        if dup:
            self.decide({"ts": ts or None, "decision": "skip",
                         "target": str(fill.get("user", ""))[:10] + "...",
                         "coin": str(fill.get("coin", "")),
                         "reason": "duplicate_fill"})
            log(f"duplicate fill dropped for {fill.get('coin')}")
            return
        self.book.apply(fill)
        px = float(fill.get("px", 0) or 0)
        if px > 0:
            self.marks[str(fill.get("coin", ""))] = px
        for intent in rolled + self.intents.flush_expired(ts):
            self.process_intent(intent)

    def process_intent(self, intent: dict) -> None:
        """One aggregated intent through the full decision path."""
        user = str(intent.get("user", "")).lower()
        coin = str(intent.get("coin", ""))
        px = float(intent.get("px", 0) or 0)
        ts = float(intent.get("time", intent.get("ts", 0)) or 0)

        def risk_ok(c, notional):
            return self.risk.check_open(c, notional, user, ts)

        def sizer(f, target):
            return size_copy(abs(float(f.get("sz", 0) or 0)), px,
                             self._target_closes(user),
                             self.cfg["hyperliquid"])

        actions = decide_fill(intent, self.targets, self.clusters,
                              self.votes, self.cfg["hyperliquid"],
                              risk_ok, sizer)
        is_open = str(intent.get("dir", "")).startswith("Open")
        for a in actions:
            self.apply_action(a, intent, shadow_ok=is_open)
        # Shadows mirror the target's exits too, whatever the
        # classification was — a skipped signal still resolves.
        if str(intent.get("dir", "")).startswith("Close"):
            self.close_shadows_for(user, coin, px, ts, "target_exit")

    # -- startup sync ------------------------------------------------------

    def startup_sync(self, user: str, positions: list[dict],
                     ts: float) -> None:
        """Match the leader's existing positions at startup.

        Paper-mode equivalent of reconcile.fetch_all_target_positions
        (MaxIsOntoSomething): seed the target book and run each existing
        position through the same decision path as a live fill, sized
        off the target's position size. Only COPY-classified, whitelisted
        coins survive decide_fill; everything else becomes a skip.
        """
        user = str(user).lower()
        label = (self.targets.get(user) or {}).get("label", user)
        for p in positions or []:
            coin = str(p.get("coin", ""))
            size = float(p.get("size", p.get("szi", 0)) or 0)
            if not coin or abs(size) <= EPS:
                continue
            self.book.set_position(user, coin, size)
            key = (user, coin)
            if key in self.positions:
                self.decide({"ts": ts or None, "decision": "skip",
                             "target": label, "coin": coin,
                             "reason": "startup_sync_already_positioned"})
                continue
            mark = self.marks.get(coin)
            if not mark or mark <= 0:
                self.decide({"ts": ts or None, "decision": "skip",
                             "target": label, "coin": coin,
                             "reason": "startup_sync_no_mark"})
                continue
            synth = {"user": user, "coin": coin,
                     "dir": "Open Long" if size > 0 else "Open Short",
                     "sz": abs(size), "px": mark, "startPosition": 0.0,
                     "ts": ts, "time": ts, "synthetic": True,
                     "fragment_count": 1}
            log(f"startup sync: {label} holds {coin} {size:+f}; mirroring")
            self.process_intent(synth)

    def apply_action(self, a: dict, fill: dict, shadow_ok: bool = True) -> None:
        kind = a["action"]
        user, coin = a.get("user", ""), a.get("coin", "")
        ts = float(a.get("ts", 0) or 0)
        if kind == "skip":
            self.decide({"ts": ts or None, "decision": "skip",
                         "target": a.get("label", user),
                         "coin": coin, "reason": a["reason"],
                         "score": a.get("score"),
                         "kelly": a.get("kelly")})
            if a.get("shadow") and shadow_ok and coin:
                px = self.marks.get(coin) or float(fill.get("px", 0) or 0)
                if px > 0:
                    self.open_shadow({**a, "ref_px": px}, fill)
            return
        if kind == "open":
            key = (user, coin)
            if key in self.positions:
                self.decide({"decision": "skip", "target": a.get("label"),
                             "coin": coin,
                             "reason": "already_positioned"})
                return
            self.positions[key] = {
                "size": a["size"] if a["side"] == "long" else -a["size"],
                "side": a["side"],
                "entry_px": a["ref_px"], "entry_ts": ts,
                "target": user, "label": a.get("label")}
            self.decide({"ts": ts or None, "decision": "open",
                         "target": a.get("label"),
                         "coin": coin, "side": a["side"], "size": a["size"],
                         "ref_px": a["ref_px"], "score": a.get("score"),
                         "kelly": a.get("kelly"),
                         "slippage_buffer_pct":
                             a.get("slippage_buffer_pct")})
            self.notifier.emit({"kind": "trade_opened", "ts": ts,
                                "target": a.get("label"), "coin": coin,
                                "side": a["side"], "size": a["size"],
                                "entry_px": a["ref_px"]})
            log(f"PAPER OPEN {coin} {a['side']} {a['size']:.6f} @ "
                f"{a['ref_px']} (copy of {a.get('label')})")
            return
        if kind == "close":
            key = (user, coin)
            pos = self.positions.get(key)
            if not pos:
                return
            # Pre-close state sync: re-read our size from the
            # authoritative source before the reduce-only close
            # (Dwellir's CRITICAL point). In paper the ledger is the
            # source; in live this becomes a fresh clearinghouseState
            # fetch.
            fresh = synced_close_size(
                lambda c: abs((self.positions.get(key) or {})
                              .get("size", 0.0)), coin)
            self.decide({"ts": ts or None, "decision": "pre_close_sync",
                         "target": pos.get("label"), "coin": coin,
                         "synced_size": round(fresh, 8)})
            self.close_position(key, pos, self.marks.get(coin), ts,
                                a.get("reason", "target_exit"),
                                pct=float(a.get("pct", 1.0)),
                                fresh_size=fresh)

    # -- cost accounting -------------------------------------------------

    def _leg_costs(self, coin: str, side: str, size: float,
                   entry_px: float, exit_px: float,
                   entry_ts: float, exit_ts: float) -> tuple[float, float]:
        """(fees_usd, funding_usd) for one closed leg.

        Fees are the resolved taker rate on entry + exit notional.
        Funding is the signed hourly accrual (positive = earned); 0.0
        when funding accounting is disabled or the history fetch
        fails. For partial closes the funding leg is approximated on
        the closed size over the full hold.
        """
        fees = self.taker_fee * size * (entry_px + exit_px)
        funding_pnl = self.funding.accrue(coin, side, size * entry_px,
                                          entry_ts, exit_ts) \
            if self.funding else 0.0
        return round(fees, 4), round(funding_pnl, 4)

    # -- shadow positions --------------------------------------------------

    def open_shadow(self, a: dict, fill: dict) -> None:
        direction = str(fill.get("dir", ""))
        side = "long" if "Long" in direction else "short"
        px = float(a.get("ref_px") or 0)
        if px <= 0:
            return
        sid = self.next_shadow
        self.next_shadow += 1
        sz = abs(float(fill.get("sz", 0) or 0))
        self.shadows[sid] = {"id": sid, "target": a.get("label", a.get("user")),
                             "coin": a["coin"], "side": side,
                             "entry_ts": float(a.get("ts", 0) or 0),
                             "entry_px": px, "size": sz,
                             "skip_reason": a.get("reason", "")}
        log(f"SHADOW #{sid} {a['coin']} {side} @ {px} "
            f"(skipped: {a.get('reason')})")

    def close_shadows_for(self, user: str, coin: str, px: float,
                          ts: float, reason: str) -> None:
        label = (self.targets.get(user) or {}).get("label", user)
        for sid, s in list(self.shadows.items()):
            if s["target"] == label and s["coin"] == coin and px > 0:
                self.close_shadow(sid, px, ts, reason)

    def close_shadow(self, sid: int, px: float, ts: float, reason: str) -> None:
        s = self.shadows.pop(sid)
        sign = 1 if s["side"] == "long" else -1
        price_pnl = (px / s["entry_px"] - 1.0) * sign \
            * s["entry_px"] * s["size"]
        fees, funding_pnl = self._leg_costs(s["coin"], s["side"],
                                            s["size"], s["entry_px"], px,
                                            s["entry_ts"], ts)
        pnl = price_pnl - fees + funding_pnl
        row = {"shadow_id": sid, "target": s["target"], "coin": s["coin"],
               "side": s["side"], "entry_ts": int(s["entry_ts"]),
               "entry_px": s["entry_px"], "size": s["size"],
               "exit_ts": int(ts), "exit_px": px, "exit_reason": reason,
               "pnl_usd": round(pnl, 4), "skip_reason": s["skip_reason"],
               "fees_usd": fees, "funding_usd": funding_pnl}
        self._append(self.shadow_path, SHADOW_FIELDS, row, True)
        log(f"SHADOW CLOSE #{sid} {s['coin']} reason={reason} "
            f"pnl {pnl:+.2f} USD (fees {fees:.4f}, funding {funding_pnl:+.4f})")

    # -- closes ------------------------------------------------------------

    def close_position(self, key: tuple[str, str], pos: dict,
                       px: float | None, ts: float, reason: str,
                       pct: float = 1.0, fresh_size: float | None = None) -> None:
        if px is None or px <= 0:
            log(f"cannot price close of {key[1]}; holding (never guess)")
            return
        held = abs(pos["size"])
        base = fresh_size if fresh_size is not None else held
        close_sz = min(base, held) * min(max(pct, 0.0), 1.0)
        if close_sz <= EPS:
            return
        sign = 1 if pos["size"] > 0 else -1
        price_pnl = (px / pos["entry_px"] - 1.0) * sign \
            * close_sz * pos["entry_px"]
        pnl_pct = (px / pos["entry_px"] - 1.0) * sign * 100.0
        fees, funding_pnl = self._leg_costs(
            key[1], "long" if sign > 0 else "short", close_sz,
            pos["entry_px"], px, pos["entry_ts"], ts)
        pnl = price_pnl - fees + funding_pnl
        row = {"trade_id": self.next_id, "mode": "paper",
               "target": pos.get("label", key[0]), "coin": key[1],
               "side": "long" if sign > 0 else "short",
               "entry_ts": int(pos["entry_ts"]), "entry_px": pos["entry_px"],
               "size": round(close_sz, 8), "exit_ts": int(ts),
               "exit_px": px, "exit_reason": reason,
               "pnl_usd": round(pnl, 4), "pnl_pct": round(pnl_pct, 4),
               "fees_usd": fees, "funding_usd": funding_pnl}
        self.next_id += 1
        self._append(self.csv_path, PAPER_FIELDS, row, True)
        self.risk.record_close(pnl, pos.get("target", ""), ts)
        self.notifier.emit({"kind": "trade_closed", "ts": ts,
                            "target": pos.get("label"), "coin": key[1],
                            "exit_reason": reason, "pnl_usd": round(pnl, 4)})
        remaining = held - close_sz
        if remaining <= EPS:
            del self.positions[key]
            self.exits.forget(key)
        else:
            pos["size"] = sign * remaining
        self.decide({"ts": int(ts) or None, "decision": "close",
                     "target": pos.get("label"),
                     "coin": key[1], "reason": reason, "pct": pct,
                     "pnl_usd": round(pnl, 4),
                     "fees_usd": fees, "funding_usd": funding_pnl})
        log(f"PAPER CLOSE {key[1]} {pct*100:.0f}% @ {px} reason={reason} "
            f"pnl {pnl:+.2f} USD (fees {fees:.4f}, funding {funding_pnl:+.4f})")

    # -- event loop --------------------------------------------------------

    def on_tick(self, ts: float) -> None:
        h = self.cfg["hyperliquid"]
        for intent in self.intents.flush_expired(ts):
            self.process_intent(intent)
        # Exits.
        for key, pos in list(self.positions.items()):
            mark = self.marks.get(key[1])
            reason = self.exits.check(key, pos["side"], pos["entry_px"],
                                     pos["entry_ts"], mark, ts)
            if reason:
                self.close_position(key, pos, mark, ts, reason)
        # Shadow exits: mirror target exits or max hold.
        max_hold = h["exits"]["max_hold_seconds"]
        for sid, s in list(self.shadows.items()):
            mark = self.marks.get(s["coin"])
            if ts - s["entry_ts"] >= max_hold and mark:
                self.close_shadow(sid, mark, ts, "max_hold")
        # Reconcile on schedule.
        if ts - self.last_reconcile >= h["mirror"]["reconcile_interval_s"]:
            self.last_reconcile = ts
            self.reconcile(ts)

    def reconcile(self, ts: float) -> None:
        from reconcile import check_drift
        # {user: {coin: signed_size}} from the target-side fill books.
        books = {u: {c: st["size"] for c, st in coins.items()}
                 for u, coins in self.book.books.items()}
        ours = {(u, c): {"size": p["size"]}
                for (u, c), p in self.positions.items()}
        for a in check_drift(ours, books):
            key = (a["user"], a["coin"])
            pos = self.positions.get(key)
            if pos:
                self.close_position(key, pos, self.marks.get(a["coin"]),
                                    ts, a["reason"], pct=a["pct"])

    def on_mark(self, coin: str, px: float, ts: float) -> None:
        if px > 0:
            self.marks[coin] = px
        # Intents close at mark time (priced at the fresh mark).
        for intent in self.intents.flush_expired(ts):
            self.process_intent(intent)
        for key, pos in list(self.positions.items()):
            if key[1] == coin:
                reason = self.exits.check(key, pos["side"], pos["entry_px"],
                                         pos["entry_ts"], px, ts)
                if reason:
                    self.close_position(key, pos, px, ts, reason)

    def run(self, source) -> int:
        import json as _json
        self.last_ts = 0.0
        for line in source:
            line = line.strip()
            if not line:
                continue
            try:
                ev = _json.loads(line)
            except _json.JSONDecodeError:
                log(f"skipping non-JSON line: {line[:80]!r}")
                continue
            kind = ev.get("type")
            ts = float(ev.get("time", ev.get("ts", 0)) or 0)
            self.last_ts = max(self.last_ts, ts)
            if kind == "fill":
                self.on_fill(ev)
            elif kind == "mark":
                self.on_mark(str(ev.get("coin", "")),
                             float(ev.get("px", 0) or 0), ts)
            elif kind == "tick":
                self.on_tick(ts)
            elif kind == "target_positions":
                self.startup_sync(str(ev.get("user", "")),
                                  ev.get("positions", []), ts)
            else:
                log(f"ignoring unknown event type: {kind!r}")
        # End of stream: flush open intents, then close shadows at last
        # marks (research data).
        for intent in self.intents.flush_all():
            self.process_intent(intent)
        for sid, s in list(self.shadows.items()):
            mark = self.marks.get(s["coin"])
            if mark:
                self.close_shadow(sid, mark, self.last_ts, "stream_end")
        log(f"stream ended; {len(self.positions)} paper positions open, "
            f"{len(self.shadows)} shadows open")
        return 0


# --------------------------------------------------------------------------
# Live gate (mirrors engine.py's philosophy)
# --------------------------------------------------------------------------

def gate_status(csv_path: str, gate_cfg: dict) -> tuple[bool, dict]:
    closed, total = 0, 0.0
    if os.path.exists(csv_path):
        with open(csv_path, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("mode") != "paper":
                    continue
                closed += 1
                try:
                    total += float(row["pnl_usd"])
                except (TypeError, ValueError):
                    pass
    ok = closed >= gate_cfg["min_closed_trades"] \
        and total >= gate_cfg["min_total_pnl_usd"]
    return ok, {"closed": closed, "total_pnl_usd": total,
                "need_closed": gate_cfg["min_closed_trades"],
                "need_pnl": gate_cfg["min_total_pnl_usd"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--fills", required=True,
                    help="NDJSON fill/mark/tick stream")
    ap.add_argument("--targets", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)
    h = cfg["hyperliquid"]
    live = h["live_trading"]

    if live:
        ok, stats = gate_status(h["paper"]["paper_trades_csv"],
                                h["paper"]["gate"])
        if not ok:
            loud("LIVE MODE REFUSED BY THE PAPER-TRADE GATE.\n"
                 f"paper record: {stats['closed']} closed trades, "
                 f"{stats['total_pnl_usd']:+.2f} USD.\n"
                 f"required: >= {stats['need_closed']} closed and "
                 f">= {stats['need_pnl']:+.2f} USD.\n"
                 "Earn the right to go live on paper first.")
            return 4
        loud("LIVE MODE REQUESTED AND GATE PASSED — but live execution "
             "is NOT wired in this scaffold (mirror.LiveExecutor raises "
             "NotImplementedError by design). Paper mode is the way.")

    targets = load_targets(args.targets)
    sc = h["scorer"]
    clusters = cluster_wallets([], sc["cluster_window_s"],
                               sc["cluster_min_coentries"])
    paper = Paper(cfg, targets, clusters)
    log(f"paper up: {len(targets)} targets, "
        f"whitelist={h['mirror']['coin_whitelist']}")
    with open(args.fills) as f:
        return paper.run(f)


if __name__ == "__main__":
    sys.exit(main())
