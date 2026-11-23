"""Stochastic + Bollinger %b: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.stochastic_bollinger import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="Stochastic + Bollinger %b",
        slug="stochastic_bollinger",
        description=(
            "John Bollinger's %b with Stochastic timing: LONG when "
            "%K crosses above %D while %b < 0.2 (price near the "
            "lower Bollinger Band) and %K < 30 — a double-oversold "
            "gate. Exit long when %b > 0.8 (upper band reached) or "
            "%K crosses below %D. Short mirror. Mean reversion "
            "into the band, not a band-breakout system."
        ),
        source_name="John Bollinger, Bollinger on Bollinger Bands (2001), %b chapter",
        source_url="https://www.bollingerbands.com/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
