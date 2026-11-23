"""Ehlers Fisher Transform trend: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.fisher_transform_trend import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Fisher Transform Trend",
        slug="fisher_transform_trend",
        description=(
            "Ehlers Fisher Transform trend: LONG when the smoothed "
            "Fisher Transform (10-bar normalized price, 0.5/0.5 "
            "smoothing) crosses above 0 from below and is rising; "
            "SHORT on the mirror cross below 0 while falling. Exit "
            "on a cross back through 0 or two consecutive bars "
            "turning against the position. The 0-cross is the "
            "trigger; the Fisher Transform near-Gaussianizes price "
            "rather than measuring momentum."
        ),
        source_name="John Ehlers, The Fisher Transform (Cybernetic Analysis for Stocks and Futures, 2004)",
        source_url="https://www.mesasoftware.com/papers/TheFisherTransform.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
