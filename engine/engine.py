#!/usr/bin/env python3
"""Paper-first copy/fade engine for Robinhood Chain.

Pipeline position: the engine is layers 3-5 of the design
(docs/STRATEGY.md): execution decisions, exits, and the paper-trade gate.

It consumes NDJSON events and acts on wallet classifications produced by
scorer/wallet_scorer.py (data/targets.json; falls back to the research
priors in data/whales_seed.json):

  COPY wallets -- a trigger with an attributed token + price opens a
                  position (paper by default);
  FADE wallets -- never followed; their buys on tokens we hold are
                  logged, and exit us only if explicitly enabled;
  PASS / watch -- ignored for trading. The scores decide, not lists.

Event types (one JSON object per line, stdin or --events FILE):
  {"type":"fomo_deposit","whale":"0x..","token":"0x..",
   "price_usdg":1.23,"ts":1759300000,"deposit_tx":".."}
      A watcher trigger. In the live pipeline the token and price are
      attributed downstream (chain_feed.py correlation + trace data);
      an unattributed trigger (no token/price) is logged and skipped --
      the engine fails closed rather than guessing what to buy.
  {"type":"mark","token":"0x..","price_usdg":1.30,"ts":...}
      A price observation; drives stop-loss / take-profit checks.
  {"type":"whale_sell","whale":"0x..","token":"0x..","ts":...}
      The copied whale sold: mirror exit (first exit rule).
  {"type":"fade_buy","whale":"0x..","token":"0x..","ts":...}
      A FADE wallet bought a token. Logged always; exits our position
      in that token only with engine.fade_exit_enabled=true.
  {"type":"tick","ts":...}
      Clock pulse for max-hold checks when no other events flow.

Exits, first trigger wins: whale mirror sell, stop-loss, take-profit,
max hold. Every close is appended to the paper-trades CSV with entry,
exit, reason and net PnL (after configured per-side gas costs) -- that
CSV is the track record the live gate reads.

THE PAPER-TRADE GATE: with engine.live_trading=true the engine refuses
to start (exit code 4) unless the CSV already holds at least
paper_gate.min_closed_trades closed trades with aggregate PnL >=
paper_gate.min_total_pnl_usdg. Even then, live execution is NOT wired
in this scaffold: the send path raises NotImplementedError until the
Robinhood Chain router wiring is verified on-chain (see contracts/).
Paper mode is the default and the intended mode for a long time.

Usage:
  solana_watcher.py | engine.py --config config.json
  engine.py --config config.example.json --events engine/examples/events.sample.ndjson \
            --targets engine/examples/targets.sample.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone

CSV_FIELDS = ["trade_id", "mode", "whale", "token", "entry_ts",
              "entry_price_usdg", "size_usdg", "gas_cost_usdg", "exit_ts",
              "exit_price_usdg", "exit_reason", "pnl_usdg", "pnl_pct"]


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[engine {ts}] {msg}", file=sys.stderr, flush=True)


def loud(msg: str) -> None:
    bar = "!" * 72
    print(f"\n{bar}\n{msg}\n{bar}\n", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Config + targets
# ---------------------------------------------------------------------------


def load_config(path: str) -> dict:
    with open(path) as f:
        cfg = json.load(f)
    eng = cfg.setdefault("engine", {})
    if "live_trading" in eng and not isinstance(eng["live_trading"], bool):
        print(f"config error: engine.live_trading must be an explicit "
              f"boolean, got {eng['live_trading']!r}. Refusing to start: "
              f"live mode is never inferred.", file=sys.stderr)
        sys.exit(2)
    return cfg


def load_targets(targets_path: str | None, seed_path: str) -> dict[str, dict]:
    """address(lower) -> {classification: copy|fade|pass, watch: bool}."""
    out: dict[str, dict] = {}
    if targets_path and os.path.exists(targets_path):
        with open(targets_path) as f:
            data = json.load(f)
        for w in data.get("wallets", []):
            out[w["address"].lower()] = {
                "classification": w["classification"],
                "watch": bool(w.get("watch"))}
        log(f"loaded {len(out)} scored targets from {targets_path}")
        return out
    if os.path.exists(seed_path):
        with open(seed_path) as f:
            seed = json.load(f)
        for w in seed.get("wallets", []):
            cls = w["classification"]
            out[w["address"].lower()] = {
                "classification": "pass" if cls in ("watch", "unrated") else cls,
                "watch": cls == "watch"}
        log(f"no targets.json; using research priors from {seed_path} "
            f"({len(out)} wallets). Run the scorer to replace these.")
        return out
    log("WARNING: no targets file found; every wallet is PASS.")
    return out


# ---------------------------------------------------------------------------
# Paper-trade gate
# ---------------------------------------------------------------------------


def paper_gate_status(csv_path: str, gate_cfg: dict) -> tuple[bool, dict]:
    closed, total_pnl = 0, 0.0
    if os.path.exists(csv_path):
        with open(csv_path, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("mode") != "paper":
                    continue
                closed += 1
                try:
                    total_pnl += float(row["pnl_usdg"])
                except (TypeError, ValueError):
                    pass
    ok = closed >= gate_cfg["min_closed_trades"] \
        and total_pnl >= gate_cfg["min_total_pnl_usdg"]
    return ok, {"closed": closed, "total_pnl_usdg": total_pnl,
                "need_closed": gate_cfg["min_closed_trades"],
                "need_pnl": gate_cfg["min_total_pnl_usdg"]}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class Engine:
    def __init__(self, cfg: dict, targets: dict[str, dict], live: bool):
        e = cfg["engine"]
        self.live = live
        self.targets = targets
        self.size = min(e["position_size_usdg"], e["max_position_usdg"])
        self.max_open = e["max_open_positions"]
        self.stop_pct = e["stop_loss_pct"]
        self.tp_pct = e["take_profit_pct"]
        self.max_hold_s = e["max_hold_seconds"]
        self.fade_exit = e.get("fade_exit_enabled", False)
        self.gas_in = e["gas_cost_per_entry_usdg"]
        self.gas_out = e["gas_cost_per_exit_usdg"]
        self.csv_path = e["paper_trades_csv"]
        self.state_path = e["state_file"]
        self.positions: dict[int, dict] = {}
        self.marks: dict[str, float] = {}
        self.next_id = 1
        self._load_state()

    # -- persistence -----------------------------------------------------

    def _load_state(self) -> None:
        if os.path.exists(self.state_path):
            with open(self.state_path) as f:
                s = json.load(f)
            self.positions = {int(k): v for k, v in s["positions"].items()}
            self.marks = s.get("marks", {})
            self.next_id = s.get("next_id", 1)
            log(f"restored {len(self.positions)} open paper positions")

    def _save_state(self) -> None:
        os.makedirs(os.path.dirname(self.state_path) or ".", exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump({"positions": self.positions, "marks": self.marks,
                       "next_id": self.next_id}, f, indent=1)

    def _append_csv(self, row: dict) -> None:
        os.makedirs(os.path.dirname(self.csv_path) or ".", exist_ok=True)
        new = not os.path.exists(self.csv_path)
        with open(self.csv_path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            if new:
                w.writeheader()
            w.writerow(row)

    # -- classification --------------------------------------------------

    def classify(self, whale: str | None) -> tuple[str, bool]:
        if not whale:
            return "pass", False
        t = self.targets.get(whale.lower())
        if t is None:
            return "pass", False
        return t["classification"], t["watch"]

    # -- position lifecycle ----------------------------------------------

    def open_position(self, whale: str, token: str, price: float, ts: float,
                      deposit_tx: str | None) -> None:
        if len(self.positions) >= self.max_open:
            log(f"skip open {token}: max open positions ({self.max_open})")
            return
        for p in self.positions.values():
            if p["whale"] == whale.lower() and p["token"] == token.lower():
                log(f"skip open {token}: already positioned with {whale}")
                return
        pid = self.next_id
        self.next_id += 1
        self.positions[pid] = {
            "id": pid, "whale": whale.lower(), "token": token.lower(),
            "entry_ts": ts, "entry_price": price, "size_usdg": self.size,
            "trigger_tx": deposit_tx}
        self.marks[token.lower()] = price
        log(f"OPEN #{pid} {token} @ {price} size {self.size} USDG "
            f"(copy of {whale})")

    def close_position(self, pid: int, price: float, ts: float, reason: str) -> None:
        p = self.positions.pop(pid)
        pnl_pct = (price / p["entry_price"] - 1.0) * 100.0
        pnl = (price / p["entry_price"] - 1.0) * p["size_usdg"] \
            - self.gas_in - self.gas_out
        row = {"trade_id": pid, "mode": "live" if self.live else "paper",
               "whale": p["whale"], "token": p["token"],
               "entry_ts": int(p["entry_ts"]), "entry_price_usdg": p["entry_price"],
               "size_usdg": p["size_usdg"],
               "gas_cost_usdg": round(self.gas_in + self.gas_out, 6),
               "exit_ts": int(ts), "exit_price_usdg": price,
               "exit_reason": reason, "pnl_usdg": round(pnl, 6),
               "pnl_pct": round(pnl_pct, 4)}
        self._append_csv(row)
        log(f"CLOSE #{pid} {p['token']} @ {price} reason={reason} "
            f"pnl {pnl:+.2f} USDG ({pnl_pct:+.2f}%)")

    # -- exit manager ------------------------------------------------------

    def check_exits(self, now: float) -> None:
        for pid, p in list(self.positions.items()):
            mark = self.marks.get(p["token"])
            if mark is None:
                continue  # cannot price it; never guess an exit price
            change = (mark / p["entry_price"] - 1.0) * 100.0
            if change <= -self.stop_pct:
                self.close_position(pid, mark, now, "stop_loss")
            elif change >= self.tp_pct:
                self.close_position(pid, mark, now, "take_profit")
            elif now - p["entry_ts"] > self.max_hold_s:
                self.close_position(pid, mark, now, "max_hold")

    # -- live execution (stubbed on purpose) -------------------------------

    def live_send_copy(self, whale: str, token: str) -> None:
        """Placeholder for the detector burst (snapshot + attemptCopy calls
        streamed across the fill window). Intentionally unwired: the
        Robinhood Chain router/PoolManager addresses in contracts/ are
        TODO-verify-on-chain, and this function must keep raising until
        that verification lands. Paper mode never reaches this path."""
        raise NotImplementedError(
            "live execution not wired: verify router wiring on-chain "
            "(contracts/src/CopyDetector.sol) before enabling")

    # -- event handling ----------------------------------------------------

    def handle(self, ev: dict) -> None:
        kind = ev.get("type")
        now = float(ev.get("ts") or ev.get("sol_timestamp") or time.time())
        if kind == "fomo_deposit":
            self.on_trigger(ev, now)
        elif kind == "mark":
            if ev.get("token") and ev.get("price_usdg"):
                self.marks[ev["token"].lower()] = float(ev["price_usdg"])
            self.check_exits(now)
        elif kind == "whale_sell":
            self.on_whale_sell(ev, now)
        elif kind == "fade_buy":
            self.on_fade_buy(ev, now)
        elif kind == "tick":
            self.check_exits(now)
        else:
            log(f"ignoring unknown event type: {kind!r}")
        self._save_state()

    def on_trigger(self, ev: dict, now: float) -> None:
        whale = ev.get("whale")
        cls, watch = self.classify(whale)
        if not whale:
            log("trigger with unattributed whale (Solana->EVM mapping is "
                "TODO-verify); skipped")
            return
        if cls == "fade":
            log(f"FADE wallet {whale} is buying; not following. "
                f"(Treating as data: log-only unless fade exits are on.)")
            if ev.get("token"):
                self.on_fade_buy({**ev, "type": "fade_buy"}, now)
            return
        if cls != "copy":
            log(f"trigger for {whale}: class={cls} watch={watch}; no trade")
            return
        token, price = ev.get("token"), ev.get("price_usdg")
        if not token or not price:
            log(f"COPY trigger for {whale} lacks token/price attribution; "
                f"skipped (fails closed)")
            return
        if self.live:
            self.live_send_copy(whale, token)  # raises until wired; loud by design
        self.open_position(whale, token, float(price), now, ev.get("deposit_tx"))

    def on_whale_sell(self, ev: dict, now: float) -> None:
        whale = (ev.get("whale") or "").lower()
        token = (ev.get("token") or "").lower()
        for pid, p in list(self.positions.items()):
            if p["whale"] == whale and p["token"] == token:
                mark = self.marks.get(token)
                if mark is None:
                    log(f"whale_sell for #{pid} but no mark to price exit; "
                        f"holding")
                    continue
                self.close_position(pid, mark, now, "whale_exit")

    def on_fade_buy(self, ev: dict, now: float) -> None:
        token = (ev.get("token") or "").lower()
        held = [pid for pid, p in self.positions.items() if p["token"] == token]
        if not held:
            return
        log(f"FADE wallet {ev.get('whale')} bought {token}, which we hold "
            f"(positions {held}); fade_exit_enabled={self.fade_exit}")
        if self.fade_exit:
            for pid in held:
                mark = self.marks.get(token)
                if mark is not None:
                    self.close_position(pid, mark, now, "fade_signal")

    # -- main loop ---------------------------------------------------------

    def run(self, source) -> None:
        for line in source:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                log(f"skipping non-JSON line: {line[:80]!r}")
                continue
            self.handle(ev)
        log(f"event stream ended; {len(self.positions)} positions still open")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--events", default=None,
                    help="NDJSON event file (default: stdin)")
    ap.add_argument("--targets", default="data/targets.json")
    ap.add_argument("--seed", default="data/whales_seed.json")
    args = ap.parse_args()

    cfg = load_config(args.config)
    eng_cfg = cfg["engine"]
    live = eng_cfg.get("live_trading", False)

    if live:
        gate = eng_cfg["paper_gate"]
        ok, stats = paper_gate_status(eng_cfg["paper_trades_csv"], gate)
        if not ok:
            loud("LIVE MODE REFUSED BY THE PAPER-TRADE GATE.\n"
                 f"paper record: {stats['closed']} closed trades, "
                 f"{stats['total_pnl_usdg']:+.2f} USDG total.\n"
                 f"required: >= {stats['need_closed']} closed and "
                 f">= {stats['need_pnl']:+.2f} USDG.\n"
                 "Earn the right to go live on paper first. "
                 "See docs/STRATEGY.md, section 4.5.")
            return 4
        loud("LIVE MODE REQUESTED AND GATE PASSED "
             f"({stats['closed']} paper trades, {stats['total_pnl_usdg']:+.2f} USDG).\n"
             "Execution is still stubbed in this scaffold and will raise "
             "NotImplementedError on the first live trigger, by design, "
             "until the router wiring is verified on-chain.")

    targets = load_targets(args.targets, args.seed)
    engine = Engine(cfg, targets, live)
    log(f"engine up: mode={'LIVE (stubbed)' if live else 'paper'}, "
        f"size={engine.size} USDG, stop {engine.stop_pct}%, "
        f"tp {engine.tp_pct}%, max hold {engine.max_hold_s}s")

    if args.events:
        with open(args.events) as f:
            engine.run(f)
    else:
        engine.run(sys.stdin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
