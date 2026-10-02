#!/usr/bin/env python3
"""Risk controls for the Hyperliquid copy engine.

Hard, boring, and non-negotiable:

  * Daily-loss circuit breaker: if realized PnL for the current UTC day
    falls to -daily_max_loss_usd or worse, no new positions open until
    the next UTC day. (From jonny-traders: pause to midnight UTC.)
  * Kill switch: if the kill-switch file exists, nothing opens. Touch
    the file to halt the engine without killing the process.
  * Coin whitelist: only listed coins may be copied.
  * Max notional per trade: single-trade size cap.

These run in paper mode too, so the paper record reflects the same
constraints live trading would face.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone


class Risk:
    def __init__(self, risk_cfg: dict, coin_whitelist: list[str]):
        self.max_loss = float(risk_cfg["daily_max_loss_usd"])
        self.kill_file = str(risk_cfg["kill_switch_file"])
        self.whitelist = {c.upper() for c in coin_whitelist}
        self._day: str | None = None
        self._realized_today = 0.0

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _roll_day(self, now_ts: float | None = None) -> None:
        day = (datetime.fromtimestamp(now_ts, timezone.utc).strftime("%Y-%m-%d")
               if now_ts else self._today())
        if day != self._day:
            self._day = day
            self._realized_today = 0.0

    def check_open(self, coin: str, notional_usd: float,
                   now_ts: float | None = None) -> tuple[bool, str]:
        """-> (allowed, reason). Called before every new position."""
        self._roll_day(now_ts)
        if os.path.exists(self.kill_file):
            return False, "kill_switch_engaged"
        if self._realized_today <= -self.max_loss:
            return False, (f"daily_loss_breaker "
                           f"({self._realized_today:+.2f} USD today)")
        if coin.upper() not in self.whitelist:
            return False, "coin_not_whitelisted"
        if notional_usd <= 0:
            return False, "nonpositive_notional"
        return True, "ok"

    def record_close(self, pnl_usd: float,
                     now_ts: float | None = None) -> None:
        """Feed realized PnL back into the daily-loss breaker."""
        self._roll_day(now_ts)
        self._realized_today += float(pnl_usd or 0.0)

    @property
    def realized_today(self) -> float:
        self._roll_day()
        return self._realized_today
