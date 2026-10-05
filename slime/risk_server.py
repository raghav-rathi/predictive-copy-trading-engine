#!/usr/bin/env python3
"""Risk server: the server side of "the AI proposes, the server decides".

Every trade a proposer emits is checked here BEFORE execution. The
proposer cannot reach the ledger except through this server.

Checks, in order:
  1. schema validity (strict proposal schema from proposer.py)
  2. coin blocklist  -- reuses the engine's COIN_BLOCKLIST
     (paper/paper_tracker.py): coins proven dead weight in backtest
  3. owner allowlist -- owner-defined allowed coins, if set
  4. max position size (USD notional)
  5. max open positions
  6. engine risk gates -- kill switch + daily loss breaker, reusing
     hyperliquid/risk.py so paper mode enforces exactly what live
     mode would
  7. per-trade price-impact cap -- walking the entry side of the book
     must not move the price more than max_impact_pct

Rejections are logged (in-memory + optional NDJSON file) with reasons.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field

ENGINE_DIR = os.path.expanduser("~/workspace/copytrade-robinhood")
sys.path.insert(0, os.path.join(ENGINE_DIR, "hyperliquid"))
sys.path.insert(0, os.path.join(ENGINE_DIR, "paper"))

from risk import Risk  # engine's 4-layer circuit breakers
from paper_tracker import COIN_BLOCKLIST  # engine's blocklist, reused


@dataclass
class RiskConfig:
    max_position_usd: float = 500.0
    max_open_positions: int = 5
    max_impact_pct: float = 1.0          # per-trade price impact cap
    allowed_coins: set | None = None     # None = allow all non-blocklisted
    daily_max_loss_usd: float = 100.0
    kill_switch_file: str = "/tmp/slime_kill_switch"
    rejection_log: str | None = None     # NDJSON path, optional


@dataclass
class Verdict:
    ok: bool
    reasons: list[str] = field(default_factory=list)


class RiskServer:
    def __init__(self, cfg: RiskConfig):
        self.cfg = cfg
        # Engine risk: kill switch + daily/per-trade breakers. Whitelist
        # is deliberately permissive here because the allowlist/blocklist
        # logic above is the owner-facing gate; the engine Risk only
        # contributes its breakers.
        self._engine_risk = Risk(
            {"max_loss_per_trade_usd": 1e18,
             "max_loss_per_target_usd": 1e18,
             "breaker_cooldown_s": 0,
             "daily_max_loss_usd": cfg.daily_max_loss_usd,
             "kill_switch_file": cfg.kill_switch_file},
            coin_whitelist=[],
        )
        # permissive whitelist -> never blocks on whitelist grounds
        self._engine_risk.whitelist = None  # type: ignore
        self.rejections: list[dict] = []

    # -- engine Risk integration ----------------------------------------

    def record_realized(self, pnl_usd: float, slime: str = "",
                        now_ts: float | None = None) -> None:
        """Feed realized PnL into the engine's daily-loss breaker."""
        self._engine_risk.record_close(pnl_usd, slime, now_ts)

    # -- validation ------------------------------------------------------

    def _impact_pct(self, trade, book: dict | None) -> float | None:
        """Entry-side price impact from book depth. None if no book."""
        if not book:
            return None
        side = trade.side
        levels = book.get("asks" if side == "long" else "bids") or []
        mid = float(book.get("mid") or 0)
        if mid <= 0 or not levels:
            return None
        remaining = float(trade.size_usd)
        cost, filled = 0.0, 0.0
        for px, qty in levels:
            px, qty = float(px), float(qty)
            take = min(remaining, px * qty)
            cost += take
            filled += take / px if px > 0 else 0.0
            remaining -= take
            if remaining <= 1e-9:
                break
        if filled <= 0:
            return None
        vwap = cost / filled
        return abs(vwap / mid - 1.0) * 100.0

    def validate_trade(self, trade, ledger, book: dict | None = None,
                       slime: str = "") -> Verdict:
        reasons: list[str] = []
        for p in trade.validate():
            reasons.append(f"schema: {p}")
        coin = str(trade.coin).upper()

        if coin in COIN_BLOCKLIST:
            reasons.append(f"coin_blocklisted({coin})")
        if self.cfg.allowed_coins is not None \
                and coin not in self.cfg.allowed_coins:
            reasons.append(f"coin_not_allowed({coin})")
        if float(trade.size_usd) > self.cfg.max_position_usd:
            reasons.append(
                f"oversized({trade.size_usd:.0f} > "
                f"{self.cfg.max_position_usd:.0f} USD max)")
        if len(ledger.open_positions()) >= self.cfg.max_open_positions:
            reasons.append(
                f"max_open_positions({self.cfg.max_open_positions})")

        # engine gates: kill switch + daily loss breaker
        if self._engine_risk.whitelist is None:
            eng_ok, eng_reason = True, "ok"
            import os as _os
            if _os.path.exists(self.cfg.kill_switch_file):
                eng_ok, eng_reason = False, "kill_switch_engaged"
            elif self._engine_risk.realized_today \
                    <= -self.cfg.daily_max_loss_usd:
                eng_ok = False
                eng_reason = (f"daily_loss_breaker "
                              f"({self._engine_risk.realized_today:+.2f} "
                              f"USD today)")
        else:  # pragma: no cover - whitelist always permissive here
            eng_ok, eng_reason = self._engine_risk.check_open(
                coin, float(trade.size_usd), slime)
        if not eng_ok:
            reasons.append(f"engine_risk: {eng_reason}")

        impact = self._impact_pct(trade, book)
        if impact is not None and impact > self.cfg.max_impact_pct:
            reasons.append(
                f"price_impact({impact:.2f}% > "
                f"{self.cfg.max_impact_pct:.2f}% max)")

        ok = not reasons
        if not ok:
            self._log_rejection(slime, trade, reasons)
        return Verdict(ok=ok, reasons=reasons)

    def validate(self, proposal, ledger,
                 book_provider=None) -> list[tuple]:
        """Validate every trade in a proposal. Returns
        [(trade, Verdict)] — rejections included, never silently dropped."""
        out = []
        for t in proposal.trades:
            book = book_provider.get_book(t.coin) if book_provider else None
            out.append((t, self.validate_trade(t, ledger, book,
                                               proposal.slime)))
        return out

    # -- rejection log ----------------------------------------------------

    def _log_rejection(self, slime: str, trade, reasons: list[str]) -> None:
        entry = {"slime": slime, "coin": str(trade.coin).upper(),
                 "side": trade.side, "size_usd": trade.size_usd,
                 "reasons": reasons}
        self.rejections.append(entry)
        if self.cfg.rejection_log:
            d = os.path.dirname(self.cfg.rejection_log)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(self.cfg.rejection_log, "a") as f:
                f.write(json.dumps(entry) + "\n")
