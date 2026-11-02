"""Aroon Oscillator: registration + re-exports."""

from strategies.aroon_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Aroon Oscillator",
        slug="aroon_oscillator",
        description=(
            "Chande Aroon oscillator (Aroon-Up minus Aroon-Down, 25 bars) zero-line cross; long on cross above 0, short below, exit on the opposite cross."
        ),
        source_name="Aroon Oscillator (Tushar Chande)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:aroon_oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
