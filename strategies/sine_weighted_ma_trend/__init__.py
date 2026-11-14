"""Sine-weighted MA trend crossover engine: registration + re-exports."""

from strategies.sine_weighted_ma_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Sine-Weighted MA Trend",
        slug="sine_weighted_ma_trend",
        description=(
            "SWMA (sine-weighted MA): weights sin(pi*(i+1)/(n+1)) over "
            "the last n closes; fast SWMA(20) vs slow SWMA(40) crossover "
            "— long on fast crossing above slow, short on fast crossing "
            "below slow, exit on the opposite cross; 2xATR stop, 3xATR "
            "chandelier trail, 200-bar max hold."
        ),
        source_name="Sine-Weighted Moving Average (Patrick Lafferty, 1999)",
        source_url="https://www.luxalgo.com/library/concept/sine-weighted-ma/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
