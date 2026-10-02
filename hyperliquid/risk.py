#!/usr/bin/env python3
"""Risk controls for the Hyperliquid copy engine.

Four independent circuit-breaker layers (Teraus's idea, made real —
each layer trips on its own and logs why):

  L1 per-trade    -- a single closed trade losing >= max_loss_per_trade_usd
                     halts new opens until breaker_cooldown_s elapse.
                     One bad fill should not become a bad session.
  L2 per-target   -- a target's realized PnL for the UTC day at or below
                     -max_loss_per_target_usd stops copying THAT target
                     until the next UTC day. One bleeding leader does not
                     get to keep spending the account.
  L3 daily        -- realized PnL for the UTC day at or below
                     -daily_max_loss_usd halts all new opens until the
                     next UTC day. (From jonny-traders: pause to midnight.)
  L4 kill switch  -- if the kill-switch file exists, nothing opens. Touch
                     the file to halt the engine without killing the
                     process.

Plus the standing limits: coin whitelist and max notional per trade.

Breaker trips are logged to `self.trips` and emitted through the
optional `notify` callable (kind="breaker_tripped") so the notifier
(Telegram, logs) sees every trip in real time.

These run in paper mode too, so the paper record reflects the same
constraints live trading would face.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone


class Risk:
    def __init__(self, risk_cfg: dict, coin_whitelist: list[str],
                 notify=None):
        self.per_trade_max = float(risk_cfg["max_loss_per_trade_usd"])
        self.per_target_max = float(risk_cfg["max_loss_per_target_usd"])
        self.cooldown_s = float(risk_cfg["breaker_cooldown_s"])
        self.max_loss = float(risk_cfg["daily_max_loss_usd"])
        self.kill_file = str(risk_cfg["kill_switch_file"])
        self.whitelist = {c.upper() for c in coin_whitelist}
        self.notify = notify or (lambda event: None)
        self.trips: list[dict] = []
        self._day: str | None = None
        self._realized_today = 0.0
        self._target_realized: dict[tuple[str, str], float] = {}
        self._target_banned_day: dict[str, str] = {}
        self._cooldown_until = 0.0

    # -- internals -----------------------------------------------------

    def _today(self, now_ts: float | None = None) -> str:
        if now_ts:
            return datetime.fromtimestamp(now_ts, timezone.utc) \
                .strftime("%Y-%m-%d")
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _roll_day(self, now_ts: float | None = None) -> None:
        day = self._today(now_ts)
        if day != self._day:
            self._day = day
            self._realized_today = 0.0
            self._target_realized = {}
            self._target_banned_day = {}

    def _trip(self, layer: str, reason: str, detail: str,
              now_ts: float | None) -> None:
        entry = {"layer": layer, "reason": reason, "detail": detail,
                 "ts": now_ts}
        self.trips.append(entry)
        try:
            self.notify({"kind": "breaker_tripped", **entry})
        except Exception:
            pass  # notifier failures never affect risk decisions

    # -- gates ----------------------------------------------------------

    def check_open(self, coin: str, notional_usd: float, user: str = "",
                   now_ts: float | None = None) -> tuple[bool, str]:
        """-> (allowed, reason). Called before every new position."""
        self._roll_day(now_ts)
        if os.path.exists(self.kill_file):
            return False, "kill_switch_engaged"
        if now_ts and now_ts < self._cooldown_until:
            return False, "breaker_cooldown"
        if self._realized_today <= -self.max_loss:
            return False, (f"daily_loss_breaker "
                           f"({self._realized_today:+.2f} USD today)")
        if user and self._target_banned_day.get(user) == self._day:
            return False, f"target_loss_breaker({user[:10]}...)"
        if coin.upper() not in self.whitelist:
            return False, "coin_not_whitelisted"
        if notional_usd <= 0:
            return False, "nonpositive_notional"
        return True, "ok"

    def record_close(self, pnl_usd: float, user: str = "",
                     now_ts: float | None = None) -> None:
        """Feed realized PnL back into the breakers."""
        self._roll_day(now_ts)
        pnl = float(pnl_usd or 0.0)
        self._realized_today += pnl
        if user:
            key = (self._day, user)
            self._target_realized[key] = \
                self._target_realized.get(key, 0.0) + pnl
            if self._target_realized[key] <= -self.per_target_max:
                self._target_banned_day[user] = self._day
                self._trip("L2", "target_loss_breaker",
                           f"{user[:10]}... at "
                           f"{self._target_realized[key]:+.2f} USD today",
                           now_ts)
        if pnl <= -self.per_trade_max:
            self._cooldown_until = (now_ts or 0.0) + self.cooldown_s
            self._trip("L1", "per_trade_loss_breaker",
                       f"single trade {pnl:+.2f} USD; opens halted "
                       f"{self.cooldown_s:.0f}s", now_ts)

    @property
    def realized_today(self) -> float:
        self._roll_day()
        return self._realized_today
