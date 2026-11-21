"""Ehlers Center of Gravity: registration + re-exports."""

from strategies.center_of_gravity import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Center of Gravity",
        slug="center_of_gravity",
        description="John Ehlers Center of Gravity: over a trailing 10-bar window of closes p[0..9] (p[0] oldest), CG = -sum((i+1)*p[i])/sum(p[i]); trigger = SMA(3) of CG. Long on a CG cross up through trigger, short on a cross down; exit on the opposite cross, plus the harness stop/trail.",
        source_name="John Ehlers, 'The CG Oscillator' (Mesa Software)",
        source_url="https://mesasoftware.com/papers/TheCGOscillator.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
