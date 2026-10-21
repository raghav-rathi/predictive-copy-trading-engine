"""Woodies CCI engine: registration + re-exports."""

from strategies.woodies_cci import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Woodies CCI",
        slug="woodies_cci",
        description=(
            "Ken Wood's Zero-Line Reject: long when CCI(14) has held "
            "above zero for 6+ bars and pulled back into [0, 50] while "
            "the fast CCI(6) turbo hooks back up through zero; short "
            "mirror on the downside; exits when CCI(14) crosses the "
            "zero line; 2xATR stop, 3xATR chandelier trail, 60-bar max "
            "hold."
        ),
        source_name="Woodies CCI (Ken Wood)",
        source_url="https://ftmo.com/fr/blog/woodies-cci-system/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
