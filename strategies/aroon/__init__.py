"""Aroon engine: registration + re-exports."""

from strategies.aroon import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande Aroon fresh-trend system",
        slug="aroon",
        description=(
            "Aroon(25); long when AroonUp >= 70 and crosses above "
            "AroonDown; short on the mirror; exit on the opposite cross."
        ),
        source_name="Tushar Chande — Aroon oscillator (1995)",
        source_url="https://www.investopedia.com/terms/a/aroon.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
