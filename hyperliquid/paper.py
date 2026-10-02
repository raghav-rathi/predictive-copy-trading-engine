#!/usr/bin/env python3
"""Paper-first runner for the Hyperliquid copy engine.

This is the default and intended mode: it replays an NDJSON fill stream
through the same decision path live trading would use (targets ->
clustering -> risk -> sizing -> mirror -> exits -> reconcile), opens
hypothetical positions, and logs everything:

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
   "sz":1.0,"px":95000.0,"startPosition":0.0,"ts":...}
  {"type":"mark","coin":"BTC","px":95100.0,"ts":...}
  {"type":"tick","ts":...}   (drives reconcile + max-hold checks)

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
from targets import load_targets, cluster_wallets, cluster_vote
from mirror import decide_fill, TargetBook, EPS
from sizing import size_copy, kelly_fstar
from exits import ExitManager
from reconcile import check_drift
from risk import Risk

PAPER_FIELDS = ["trade_id", "mode", "target", "coin", "side", "entry_ts",
                "entry_px", "size", "exit_ts", "exit_px", "exit_reason",
                "pnl_usd", "pnl_pct"]
SHADOW_FIELDS = ["shadow_id", "target", "coin", "side", "entry_ts",
                 "entry_px", "size", "exit_ts", "exit_px", "exit_reason",
                 "pnl_usd", "skip_reason"]


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
        self.positions: dict[tuple[str, str], dict] = {}
        self.marks: dict[str, float] = {}
        self.shadows: dict[int, dict] = {}
        self.risk = Risk(h["risk"], h["mirror"]["coin_whitelist"])
        self.exits = ExitManager(h["exits"]["stop_loss_pct"],
                                 h["exits"]["take_profit_pct"],
                                 h["exits"]["max_hold_seconds"])
        self.next_id = 1
        self.next_shadow = 1
        self.last_reconcile = 0.0
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
        self.book.apply(fill)
        user = str(fill.get("user", "")).lower()
        coin = str(fill.get("coin", ""))
        px = float(fill.get("px", 0) or 0)
        ts = float(fill.get("time", fill.get("ts", 0)) or 0)
        if px > 0:
            self.marks[coin] = px

        def risk_ok(c, notional):
            return self.risk.check_open(c, notional, ts)

        def sizer(f, target):
            return size_copy(abs(float(f.get("sz", 0) or 0)), px,
                             self._target_closes(user),
                             self.cfg["hyperliquid"])

        actions = decide_fill(fill, self.targets, self.clusters,
                              self.votes, self.cfg["hyperliquid"],
                              risk_ok, sizer)
        is_open = str(fill.get("dir", "")).startswith("Open")
        for a in actions:
            self.apply_action(a, fill, shadow_ok=is_open)
        # Shadows mirror the target's exits too, whatever the
        # classification was — a skipped signal still resolves.
        if str(fill.get("dir", "")).startswith("Close"):
            self.close_shadows_for(user, coin, px, ts, "target_exit")

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
                "entry_px": a["ref_px"], "entry_ts": ts,
                "target": user, "label": a.get("label")}
            self.decide({"ts": ts or None, "decision": "open",
                         "target": a.get("label"),
                         "coin": coin, "side": a["side"], "size": a["size"],
                         "ref_px": a["ref_px"], "score": a.get("score"),
                         "kelly": a.get("kelly"),
                         "slippage_buffer_pct":
                             a.get("slippage_buffer_pct")})
            log(f"PAPER OPEN {coin} {a['side']} {a['size']:.6f} @ "
                f"{a['ref_px']} (copy of {a.get('label')})")
            return
        if kind == "close":
            key = (user, coin)
            pos = self.positions.get(key)
            if not pos:
                return
            self.close_position(key, pos, self.marks.get(coin), ts,
                                a.get("reason", "target_exit"),
                                pct=float(a.get("pct", 1.0)))

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
        pnl = (px / s["entry_px"] - 1.0) * sign * s["entry_px"] * s["size"]
        row = {"shadow_id": sid, "target": s["target"], "coin": s["coin"],
               "side": s["side"], "entry_ts": int(s["entry_ts"]),
               "entry_px": s["entry_px"], "size": s["size"],
               "exit_ts": int(ts), "exit_px": px, "exit_reason": reason,
               "pnl_usd": round(pnl, 4), "skip_reason": s["skip_reason"]}
        self._append(self.shadow_path, SHADOW_FIELDS, row, True)
        log(f"SHADOW CLOSE #{sid} {s['coin']} reason={reason} "
            f"pnl {pnl:+.2f} USD")

    # -- closes ------------------------------------------------------------

    def close_position(self, key: tuple[str, str], pos: dict,
                       px: float | None, ts: float, reason: str,
                       pct: float = 1.0) -> None:
        if px is None or px <= 0:
            log(f"cannot price close of {key[1]}; holding (never guess)")
            return
        close_sz = abs(pos["size"]) * min(max(pct, 0.0), 1.0)
        if close_sz <= EPS:
            return
        sign = 1 if pos["size"] > 0 else -1
        pnl = (px / pos["entry_px"] - 1.0) * sign * close_sz * pos["entry_px"]
        pnl_pct = (px / pos["entry_px"] - 1.0) * sign * 100.0
        row = {"trade_id": self.next_id, "mode": "paper",
               "target": pos.get("label", key[0]), "coin": key[1],
               "side": "long" if sign > 0 else "short",
               "entry_ts": int(pos["entry_ts"]), "entry_px": pos["entry_px"],
               "size": round(close_sz, 8), "exit_ts": int(ts),
               "exit_px": px, "exit_reason": reason,
               "pnl_usd": round(pnl, 4), "pnl_pct": round(pnl_pct, 4)}
        self.next_id += 1
        self._append(self.csv_path, PAPER_FIELDS, row, True)
        self.risk.record_close(pnl, ts)
        remaining = abs(pos["size"]) - close_sz
        if remaining <= EPS:
            del self.positions[key]
        else:
            pos["size"] = sign * remaining
        self.decide({"ts": int(ts) or None, "decision": "close",
                     "target": pos.get("label"),
                     "coin": key[1], "reason": reason, "pct": pct,
                     "pnl_usd": round(pnl, 4)})
        log(f"PAPER CLOSE {key[1]} {pct*100:.0f}% @ {px} reason={reason} "
            f"pnl {pnl:+.2f} USD")

    # -- event loop --------------------------------------------------------

    def on_tick(self, ts: float) -> None:
        h = self.cfg["hyperliquid"]
        # Exits.
        for key, pos in list(self.positions.items()):
            mark = self.marks.get(key[1])
            reason = self.exits.check(pos["entry_px"], pos["entry_ts"],
                                     mark, ts)
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
        for key, pos in list(self.positions.items()):
            if key[1] == coin:
                reason = self.exits.check(pos["entry_px"], pos["entry_ts"],
                                         px, ts)
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
            else:
                log(f"ignoring unknown event type: {kind!r}")
        # End of stream: close shadows at last marks (research data).
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


def loud(msg: str) -> None:
    bar = "!" * 72
    print(f"\n{bar}\n{msg}\n{bar}\n", file=sys.stderr, flush=True)


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
