"""Elder Force Index engine: registration + re-exports."""

from strategies.elder_force_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Force Index",
        slug="elder_force_index",
        description=(
            "Elder Force Index pullback timing: long when fi13 > 0 "
            "(bulls in charge) and fi2 crosses below zero (the dip), "
            "short on the mirror; exits when fi13 itself crosses zero "
            "(balance of power flipped); 2xATR stop, 3xATR trail, "
            "100-bar max hold."
        ),
        source_name="Force Index (Alexander Elder, Trading for a Living)",
        source_url="https://www.luxalgo.com/library/concept/force-index/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
