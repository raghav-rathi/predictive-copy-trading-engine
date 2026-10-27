"""Ehlers SineWave: registration + re-exports."""

from strategies.ehlers_sinewave import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers SineWave",
        slug="ehlers_sinewave",
        description=(
            "Even Better SineWave (Ehlers): sine/lead-sine cross in cycle mode; long on sine crossing above lead sine, short on crossing below."
        ),
        source_name="John Ehlers SineWave / Even Better Sinewave (MESA)",
        source_url="https://www.quantconnect.com/forum/discussion/940/john-ehlers-sine-wave-indicator/p1",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
