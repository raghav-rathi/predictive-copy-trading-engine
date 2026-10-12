"""Pivot breakout engine: registration + re-exports."""

from strategies.pivot_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Floor-Trader Pivot Breakout (R1/S1)",
        slug="pivot_breakout",
        description=(
            "Classic floor pivots from prior UTC-day OHLC: long on 1h close "
            "breaking above prior R1, short below prior S1, exit on touch of "
            "the opposite side or 2xATR hard stop."
        ),
        source_name="Pivot Point (floor-trader pivots) — Investopedia",
        source_url="https://www.investopedia.com/terms/p/pivotpoint.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
