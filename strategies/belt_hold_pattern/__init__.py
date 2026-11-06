"""Belt Hold Pattern: registration + re-exports."""

from strategies.belt_hold_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Belt Hold Pattern",
        slug="belt_hold_pattern",
        description="Steve Nison belt hold: a tall white candle opening on its low after a downtrend (long) or a long black candle opening on its high after an uptrend (short); body >= 60% of range, open within 10% of the range of the extreme, little/no shadow on the far side. Exit on the opposite belt hold.",
        source_name="Steve Nison — Belt Hold (Japanese Candlestick Charting Techniques, 1991)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
