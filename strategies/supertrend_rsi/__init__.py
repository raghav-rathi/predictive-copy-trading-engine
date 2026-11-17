"""Supertrend + RSI: registration + re-exports."""

from strategies.supertrend_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Supertrend RSI",
        slug="supertrend_rsi",
        description="Supertrend(10, 3.0) + Wilder RSI(14): long when the close is above the Supertrend line and RSI crosses above 50, short when the close is below the line and RSI crosses below 50; exit on the Supertrend direction flip, plus the harness stop/trail.",
        source_name="Supertrend (Olivier Seban) + Wilder RSI",
        source_url="https://www.investopedia.com/supertrend-indicator-7976167",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
