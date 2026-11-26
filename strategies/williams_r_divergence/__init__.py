"""Williams %R divergence engine: registration + re-exports."""

from strategies.williams_r_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Williams %R Divergence",
        slug="williams_r_divergence",
        description=(
            "Larry Williams %R(14) regular divergence on "
            "confirmed ±2-bar pivots: long on a bullish "
            "divergence (lower pivot low, higher %R, %R < -80 "
            "at the pivot), short on the mirror (%R > -20); "
            "exit on a %R cross back through -50 or the "
            "opposite divergence; 2xATR stop, 3xATR trail, "
            "120-bar max hold."
        ),
        source_name="Larry Williams — Williams %R divergence",
        source_url="https://en.wikipedia.org/wiki/Williams_%R",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
