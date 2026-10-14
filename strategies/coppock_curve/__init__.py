"""Coppock Curve engine: registration + re-exports."""

from strategies.coppock_curve import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Coppock Curve zero-cross system",
        slug="coppock_curve",
        description=(
            "Coppock = WMA(10) of ROC(14)+ROC(11); long when it crosses "
            "above zero from below, short on the mirror cross below zero; "
            "exit on the opposite cross."
        ),
        source_name="E.S. Coppock — Coppock Curve (Barron's, 1962)",
        source_url="https://en.wikipedia.org/wiki/Coppock_curve",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
