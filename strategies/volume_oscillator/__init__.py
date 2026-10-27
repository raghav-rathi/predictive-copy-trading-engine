"""Volume Oscillator: registration + re-exports."""

from strategies.volume_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume Oscillator",
        slug="volume_oscillator",
        description=(
            "Volume Oscillator (5/10): long on the oscillator crossing above zero while price is above its 20-bar average; short on crossing below zero while price is below it; exit on the opposite cross."
        ),
        source_name="Volume Oscillator (Buff Dormeier / volume-analysis canon)",
        source_url="https://www.investopedia.com/terms/v/volume-oscillator.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
