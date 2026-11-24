"""Premium/discount engine: registration + re-exports."""

from strategies.premium_discount import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Premium/Discount",
        slug="premium_discount",
        description=(
            "ICT premium/discount equilibrium: long when close "
            "crosses above the 48-bar range midpoint after the low "
            "touched the discount zone in the last 12 bars; short "
            "mirror after a premium touch; exit on the opposite "
            "equilibrium cross; 2xATR stop, 3xATR trail, 60-bar max "
            "hold."
        ),
        source_name="ICT premium/discount (Michael Huddleston)",
        source_url="https://www.luxalgo.com/library/concept/premium-and-discount/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
