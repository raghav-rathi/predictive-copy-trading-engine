"""Laguerre filter trend engine: registration + re-exports."""

from strategies.laguerre_filter_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Laguerre Filter Trend",
        slug="laguerre_filter_trend",
        description=(
            "Laguerre filter (Ehlers, gamma=0.8) on hl2: four-element "
            "recursive filter, Filt=(L0+2*L1+2*L2+L3)/6; long when close "
            "crosses above Filt and Filt is rising, short when close "
            "crosses below Filt and Filt is falling, exit on the "
            "opposite cross; 2xATR stop, 3xATR chandelier trail, "
            "200-bar max hold."
        ),
        source_name="Laguerre Filter (John Ehlers)",
        source_url="https://efs.kb.esignal.com/hc/en-us/articles/6362941110555-Four-Element-Laguerre-Filter-by-John-Ehlers",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
