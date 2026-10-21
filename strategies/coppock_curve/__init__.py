"""Coppock Curve engine: registration + re-exports."""

from strategies.coppock_curve import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Coppock Curve",
        slug="coppock_curve",
        description=(
            "Coppock curve (ROC(14)+ROC(11) smoothed with a 10-bar "
            "linear WMA): long when the curve crosses above zero, "
            "short when it crosses below; exits on the opposite "
            "cross; 2xATR stop, 3xATR chandelier trail, 200-bar max "
            "hold."
        ),
        source_name="Coppock Curve (E.S.C. Coppock, 1962)",
        source_url="https://en.wikipedia.org/wiki/Coppock_curve",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
