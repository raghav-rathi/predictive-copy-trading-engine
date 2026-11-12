"""Ergodic Oscillator: registration + re-exports."""

from strategies.ergodic_indicator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ergodic Oscillator",
        slug="ergodic_indicator",
        description="William Blau's ergodic oscillator (Momentum, Direction, and Divergence, 1995): 100 x double-smoothed momentum / double-smoothed absolute momentum (25/13) with a 7-bar signal line. Long on the ergodic crossing above its signal line, short on the cross below; exit on the opposite cross, with the harness stop/trail as the exit mechanism.",
        source_name="William Blau — Ergodic Oscillator / True Strength Index, Momentum, Direction, and Divergence (1995)",
        source_url="https://www.luxalgo.com/library/concept/ergodic-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
