"""Balanced Price Range: registration + re-exports."""

from strategies.balanced_price_range import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Balanced Price Range",
        slug="balanced_price_range",
        description="ICT Balanced Price Range: a BPR forms where a bullish and a bearish fair value gap overlap within 60 bars; direction follows the later gap; enter on the first close back inside the overlap zone after price traded beyond it; exit on a close through the zone or the opposite signal, plus the harness stop/trail.",
        source_name="ICT Balanced Price Range (Inner Circle Trader)",
        source_url="https://innercircletrader.net/tutorials/ict-balanced-price-range-bpr/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
