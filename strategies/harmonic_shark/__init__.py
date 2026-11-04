"""Harmonic Shark: registration + re-exports."""

from strategies.harmonic_shark import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Harmonic Shark",
        slug="harmonic_shark",
        description="Harmonic Shark pattern (Scott Carney): five swing points X-A-B-C-D whose leg ratios fall in the Shark bands (B 0.332-0.668 of XA, C 1.08-1.668 of AB, D 0.836-1.18 of XA). Entry at D completion (reversal), exit on the opposite pattern plus ATR stop / trail.",
        source_name="Harmonic Shark pattern (Scott Carney)",
        source_url="https://www.ebc.com/forex/harmonic-patterns",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
