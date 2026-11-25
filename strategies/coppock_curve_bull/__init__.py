"""Coppock Curve engine: registration + re-exports."""

from strategies.coppock_curve_bull import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Coppock Curve Bull",
        slug="coppock_curve_bull",
        description=(
            "Edwin Coppock's Coppock Curve (Barron's, Oct 15, 1962), "
            "translated from monthly to 1h bars (ROC 336h + ROC 264h, "
            "WMA 240h): long on the canonical below-zero hook "
            "(curve turns up while negative), short on the mirror "
            "extension; exit on the opposite turn or a zero cross "
            "against the position; 2xATR stop, 3xATR trail, 240-bar "
            "max hold."
        ),
        source_name="Edwin Coppock, Coppock Curve (Barron's, Oct 15, 1962)",
        source_url="https://en.wikipedia.org/wiki/Coppock_curve",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
