#!/usr/bin/env python3
"""Transaction preview: decode the trade BEFORE anything is signed.

Slime Family rule: every transaction is previewed -- who pays, margin,
fees, liquidation price, worst-case loss -- before signing. In paper
mode the preview is logged and the trade executes against the paper
ledger; the code path is IDENTICAL for live, which stays gated (the
live executor raises NotImplementedError by design -- see
hyperliquid/mirror.py -- and the slime runner refuses live mode).
"""
from __future__ import annotations

from dataclasses import dataclass

TAKER_FEE = 0.00035     # Hyperliquid taker fee per side
SLIPPAGE_ASSUMPTION = 0.00020
MMR = 0.03              # maintenance margin ratio approximation


@dataclass
class PreviewConfig:
    leverage: float = 5.0
    fee_rate: float = TAKER_FEE
    slippage: float = SLIPPAGE_ASSUMPTION


def liquidation_price(entry_px: float, side: str,
                      leverage: float) -> float:
    """Estimate: liq where losses consume margin minus maintenance.
    Long: entry*(1 - 1/lev + MMR); short: entry*(1 + 1/lev - MMR)."""
    if side == "long":
        return entry_px * (1.0 - 1.0 / leverage + MMR)
    return entry_px * (1.0 + 1.0 / leverage - MMR)


def preview_trade(coin: str, side: str, size_usd: float, entry_px: float,
                  equity_usd: float, open_positions: int,
                  cfg: PreviewConfig = PreviewConfig()) -> dict:
    """-> {margin required, estimated fees, liquidation price,
    worst-case loss, position after trade}. Pure function: the exact
    same dict is produced in paper and (gated) live paths."""
    notional = float(size_usd)
    margin = notional / cfg.leverage
    fees = notional * (cfg.fee_rate + cfg.slippage) * 2  # round trip
    liq = liquidation_price(entry_px, side, cfg.leverage)
    worst_case = margin + fees  # full liquidation + round-trip costs
    return {
        "coin": coin.upper(),
        "side": side,
        "notional_usd": round(notional, 2),
        "entry_px": entry_px,
        "leverage": cfg.leverage,
        "margin_required_usd": round(margin, 2),
        "estimated_fees_usd": round(fees, 2),
        "liquidation_px": round(liq, 4),
        "worst_case_loss_usd": round(worst_case, 2),
        "equity_after_margin_usd": round(equity_usd - margin, 2),
        "open_positions_after": open_positions + 1,
        "margin_pct_of_equity": round(margin / equity_usd * 100, 2)
        if equity_usd > 0 else 0.0,
    }
