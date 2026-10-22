"""Ehlers SuperSmoother trend engine: registration + re-exports."""

from strategies.ehlers_supersmoother import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SuperSmoother Trend",
        slug="ehlers_supersmoother",
        description=(
            "Ehlers' 2-pole SuperSmoother(20): long when close crosses "
            "above the filter while the filter is rising, short on a "
            "cross below while it is falling; exits on the opposite "
            "cross; 2xATR stop, 2xATR chandelier trail, 150-bar max hold."
        ),
        source_name="SuperSmoother (John Ehlers)",
        source_url="https://forex-station.com/post1295578265.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
