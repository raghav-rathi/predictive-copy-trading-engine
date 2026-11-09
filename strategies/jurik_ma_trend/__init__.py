"""Jurik MA trend: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.jurik_ma_trend import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Jurik MA Trend",
        slug="jurik_ma_trend",
        description="Jurik Moving Average (length 14, phase 50, public three-stage volty-based reconstruction): long when the close crosses above the JMA and the JMA is rising, short on the mirror cross with a falling JMA; exit on a cross back.",
        source_name="Wickra docs — JMA (public three-stage reconstruction); Forex-Station — Jurik JMA Algorithm Revealed",
        source_url="https://docs.wickra.org/Indicators/Indicator-Jma",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
