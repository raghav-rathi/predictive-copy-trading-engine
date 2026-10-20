"""Volume Profile Value-Area Fade: registration + re-exports."""

from strategies.volume_profile import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume Profile Value-Area Fade",
        slug="volume_profile",
        description=(
            "Rolling 168-bar composite volume profile in 24 price bins; "
            "each bar's volume spread uniformly over the bins its range "
            "touches. POC = max-volume bin; value area expands outward "
            "from the POC to >= 70% of window volume -> VAH/VAL. Long "
            "when the prior close dipped below VAL and the current "
            "close reclaims it (failed breakdown); short symmetric on "
            "failed breakouts above VAH. No signal exits — 2xATR stop, "
            "3xATR target (VAL->VAH rotation proxy), 120-bar max hold."
        ),
        source_name="Volume profile POC/VAH/VAL (markettrace.ai)",
        source_url="https://markettrace.ai/blog/volume-profile-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
