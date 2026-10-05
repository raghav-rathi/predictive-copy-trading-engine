#!/usr/bin/env python3
"""Watchdog: the independent per-minute stops loop.

Slime Family rule: stops are checked FIRST, and every minute between
turns, even while the agent sleeps. This loop runs on its OWN timer
against open paper positions and does not depend on the proposer:
if the proposer is idle/asleep, stops still fire.

Exit logic reuses the engine's ExitManager (hyperliquid/exits.py) --
stop loss, take profit, trailing stop -- so slime stops behave exactly
like engine stops. Max-hold/age are carried through too.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field

ENGINE_DIR = os.path.expanduser("~/workspace/copytrade-robinhood")
sys.path.insert(0, os.path.join(ENGINE_DIR, "hyperliquid"))

from exits import ExitManager  # engine exits, reused not duplicated


@dataclass
class WatchdogConfig:
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 6.0
    trailing_stop_pct: float = 1.0
    max_hold_seconds: float = 24 * 3600
    interval_s: float = 60.0


class Watchdog:
    """Independent stops checker. Owns an engine ExitManager; the
    caller supplies fresh marks and a close callback."""

    def __init__(self, cfg: WatchdogConfig):
        self.cfg = cfg
        self.exits = ExitManager(
            stop_loss_pct=cfg.stop_loss_pct,
            take_profit_pct=cfg.take_profit_pct,
            max_hold_seconds=cfg.max_hold_seconds,
            trailing_stop_pct=cfg.trailing_stop_pct,
        )
        self.fired: list[dict] = []  # every stop event, for the board

    def check(self, positions: dict, marks: dict[str, float],
              now: float) -> list[tuple[str, str]]:
        """One stops sweep over open positions. Returns
        [(position_key, exit_reason)] for everything that must close.
        Positions: {key: {"side", "entry_px", "entry_ts", ...}}."""
        hits = []
        for key, pos in positions.items():
            mark = marks.get(pos["coin"])
            reason = self.exits.check(key, pos["side"], pos["entry_px"],
                                     pos["entry_ts"], mark, now)
            if reason:
                hits.append((key, reason))
                self.fired.append({"key": key, "coin": pos["coin"],
                                   "side": pos["side"], "reason": reason,
                                   "mark": mark, "ts": now})
        return hits

    def forget(self, key) -> None:
        self.exits.forget(key)

    def run_forever(self, get_positions, get_marks, on_stop) -> None:
        """Own timer: stops-first sweep every interval_s, forever.
        `on_stop(key, reason)` performs the close (paper ledger)."""
        while True:
            now = time.time()
            for key, reason in self.check(get_positions(),
                                         get_marks(), now):
                on_stop(key, reason)
            time.sleep(self.cfg.interval_s)
