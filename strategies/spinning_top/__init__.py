"""Spinning top engine: registration + re-exports."""

from strategies.spinning_top import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Spinning Top",
        slug="spinning_top",
        description=(
            "Steve Nison spinning top reversal at swing extremes: "
            "long on a spinning top (body <= 30% of range, both "
            "wicks >= 30%) whose low reaches the prior 20-bar low; "
            "short mirror at the prior 20-bar high; exit on the "
            "opposite signal; 2xATR stop, 3xATR trail, 60-bar max "
            "hold."
        ),
        source_name='Steve Nison, "Japanese Candlestick Charting Techniques" (spinning top)',
        source_url="https://www.candelacharts.com/patterns/spinning-top",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
