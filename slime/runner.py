#!/usr/bin/env python3
"""Slime loop: stops first -> read market -> think -> server check ->
preview -> execute in PAPER MODE -> post to board.

PAPER-ONLY DISCLAIMER: this module refuses to run in live mode. Live
execution stays unwired by design (hyperliquid/mirror.py's LiveExecutor
raises NotImplementedError). Paper results are simulated and are NOT
evidence of live edge.

One loop step:
  1. STOPS FIRST -- watchdog sweep over open paper positions, even if
     the proposers are about to be skipped (quiet turn) or asleep.
  2. READ MARKET -- snapshot from the feed (mids, changes, funding,
     whale flow).
  3. QUIET TURN -- if nothing moved since the last turn, skip thinking
     entirely (stops were still checked in step 1).
  4. THINK -- each slime proposes (strict schema; AI proposes only).
  5. SERVER CHECK -- risk server validates every trade; sell-back check
     on survivors.
  6. PREVIEW -- margin/fees/liquidation/worst-case, logged.
  7. EXECUTE (paper) -- ledger updated at mid.
  8. BOARD -- proposal, verdicts, execution, stops all posted.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from .proposer import MarketSnapshot, Proposal, SPECIES
from .risk_server import RiskServer, RiskConfig
from .sellback import (sellback_ok, SellbackConfig, BookFeed,
                       StubBookFeed)
from .watchdog import Watchdog, WatchdogConfig
from .preview import preview_trade, PreviewConfig
from .board import Board


@dataclass
class LoopConfig:
    equity_usd: float = 10_000.0
    risk: RiskConfig = field(default_factory=RiskConfig)
    sellback: SellbackConfig = field(default_factory=SellbackConfig)
    watchdog: WatchdogConfig = field(default_factory=WatchdogConfig)
    preview: PreviewConfig = field(default_factory=PreviewConfig)
    quiet_move_pct: float = 0.15   # skip thinking below this max 1h move
    board_path: str = "slime/board/board.ndjson"
    live_mode: bool = False        # NEVER set True: refused below


class PaperLedger:
    """In-memory paper positions + equity. Paper only."""

    def __init__(self, equity_usd: float):
        self.equity = float(equity_usd)
        self.positions: dict[str, dict] = {}  # key "slime:COIN"
        self.realized = 0.0

    def open_positions(self) -> dict:
        return self.positions

    def open(self, slime: str, coin: str, side: str, size_usd: float,
             px: float, ts: float, preview: dict) -> str:
        key = f"{slime}:{coin.upper()}"
        self.positions[key] = {
            "key": key, "slime": slime, "coin": coin.upper(),
            "side": side, "size_usd": float(size_usd),
            "size_coin": float(size_usd) / px if px > 0 else 0.0,
            "entry_px": px, "entry_ts": ts, "preview": preview,
        }
        return key

    def close(self, key: str, px: float, ts: float,
              reason: str) -> dict | None:
        pos = self.positions.pop(key, None)
        if not pos or px <= 0:
            return None
        sign = 1 if pos["side"] == "long" else -1
        pnl = (px / pos["entry_px"] - 1.0) * sign * pos["size_usd"]
        fees = pos["size_usd"] * 0.00055 * 2
        net = pnl - fees
        self.realized += net
        self.equity += net
        return {"key": key, "slime": pos["slime"], "coin": pos["coin"],
                "side": pos["side"], "size_usd": pos["size_usd"],
                "entry_px": pos["entry_px"], "exit_px": px,
                "exit_ts": ts, "reason": reason,
                "pnl_usd": round(net, 2)}


class SlimeLoop:
    def __init__(self, cfg: LoopConfig, feed: BookFeed,
                 market_fn, slime_names: list[str] | None = None):
        if cfg.live_mode:
            raise RuntimeError(
                "LIVE MODE REFUSED: the slime loop is paper-only. Live "
                "execution is not wired (mirror.LiveExecutor raises "
                "NotImplementedError by design).")
        self.cfg = cfg
        self.feed = feed
        self.market_fn = market_fn  # () -> MarketSnapshot
        names = slime_names or list(SPECIES)
        self.slimes = {n: SPECIES[n]() for n in names}
        self.risk = RiskServer(cfg.risk)
        self.watchdog = Watchdog(cfg.watchdog)
        self.ledger = PaperLedger(cfg.equity_usd)
        self.board = Board(cfg.board_path)
        self._last_sig: str | None = None
        self.turns = 0
        self.quiet_turns = 0

    # -- loop -----------------------------------------------------------

    @staticmethod
    def _sig(market: MarketSnapshot) -> str:
        blob = json.dumps({c: round(p, 6)
                           for c, p in sorted(market.mids.items())},
                          sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]

    def _stops_first(self, market: MarketSnapshot) -> None:
        now = market.ts
        marks = dict(market.mids)
        for key, reason in self.watchdog.check(self.ledger.positions,
                                               marks, now):
            filled = self.ledger.close(key, marks.get(
                self.ledger.positions[key]["coin"], 0.0), now, reason)
            self.watchdog.forget(key)
            if filled:
                self.risk.record_realized(filled["pnl_usd"],
                                          filled["slime"], now)
                self.board.post({"type": "stop", **filled})
                self.board.post({"type": "execution", "action": "close",
                                 **filled})

    def step(self) -> dict:
        """One full loop step. Returns a summary dict."""
        self.turns += 1
        market = self.market_fn()

        # 1. STOPS FIRST -- always, even on quiet turns.
        self._stops_first(market)

        # 2-3. Quiet turn: nothing moved -> skip thinking.
        sig = self._sig(market)
        if sig == self._last_sig:
            self.quiet_turns += 1
            return {"turn": self.turns, "quiet": True,
                    "positions": len(self.ledger.positions)}
        self._last_sig = sig
        max_move = max((abs(c) for c in market.chg_1h.values()),
                       default=0.0)
        if self._last_sig and max_move < self.cfg.quiet_move_pct \
                and self.turns > 1:
            # market snapshot changed only by dust; still a quiet turn
            pass  # fall through: sig changed, so think anyway

        # 4. THINK -- each slime proposes.
        summary = {"turn": self.turns, "quiet": False,
                   "proposals": [], "accepted": 0, "rejected": 0}
        for name, slime in self.slimes.items():
            proposal: Proposal = slime.propose(market)
            problems = proposal.validate()
            self.board.post({
                "type": "proposal", "slime": name,
                "thought": proposal.thought,
                "trades": [t.__dict__ for t in proposal.trades],
                "snapshot_id": proposal.snapshot_id,
                "schema_problems": problems,
            })
            if problems:
                summary["rejected"] += len(proposal.trades)
                continue
            # 5. SERVER CHECK -- risk server, then sell-back.
            for trade, verdict in self.risk.validate(proposal,
                                                     self.ledger,
                                                     self.feed):
                if not verdict.ok:
                    summary["rejected"] += 1
                    self.board.post({
                        "type": "verdict", "slime": name,
                        "coin": trade.coin, "side": trade.side,
                        "size_usd": trade.size_usd,
                        "verdict": "REJECTED",
                        "reasons": verdict.reasons,
                        "thought": proposal.thought,
                    })
                    continue
                ok, detail = sellback_ok(trade.coin, trade.side,
                                         trade.size_usd,
                                         self.feed.get_book(trade.coin),
                                         self.cfg.sellback)
                if not ok:
                    summary["rejected"] += 1
                    self.board.post({
                        "type": "verdict", "slime": name,
                        "coin": trade.coin, "side": trade.side,
                        "size_usd": trade.size_usd,
                        "verdict": "REJECTED",
                        "reasons": [f"sellback: {detail['reason']}"],
                        "thought": proposal.thought,
                    })
                    continue
                # 6. PREVIEW -- identical code path for live (gated).
                mid = market.mids.get(trade.coin.upper(), 0.0)
                if mid <= 0:
                    continue
                pv = preview_trade(trade.coin, trade.side,
                                   trade.size_usd, mid,
                                   self.ledger.equity,
                                   len(self.ledger.positions),
                                   self.cfg.preview)
                self.board.post({
                    "type": "verdict", "slime": name,
                    "coin": trade.coin, "side": trade.side,
                    "size_usd": trade.size_usd,
                    "verdict": "ACCEPTED", "preview": pv,
                    "thought": proposal.thought,
                })
                # 7. EXECUTE -- paper ledger only.
                key = f"{name}:{trade.coin.upper()}"
                if key in self.ledger.positions:
                    continue  # one position per slime+coin
                self.ledger.open(name, trade.coin, trade.side,
                                 trade.size_usd, mid, market.ts, pv)
                summary["accepted"] += 1
                self.board.post({
                    "type": "execution", "action": "open", "slime": name,
                    "coin": trade.coin.upper(), "side": trade.side,
                    "size_usd": trade.size_usd, "entry_px": mid,
                    "preview": pv, "thought": proposal.thought,
                })
            summary["proposals"].append(name)
        summary["positions"] = len(self.ledger.positions)
        summary["realized"] = round(self.ledger.realized, 2)
        return summary

    def run(self, steps: int, step_s: float = 0.0):
        for _ in range(steps):
            s = self.step()
            print(f"[slime] turn {s['turn']}: "
                  f"{'QUIET' if s.get('quiet') else 'thinked'} "
                  f"accepted={s.get('accepted', 0)} "
                  f"rejected={s.get('rejected', 0)} "
                  f"positions={s['positions']} "
                  f"realized={self.ledger.realized:+.2f}")
            if step_s:
                time.sleep(step_s)
