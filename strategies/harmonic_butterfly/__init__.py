"""Harmonic Butterfly: registration + re-exports."""

from strategies.harmonic_butterfly import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Harmonic Butterfly",
        slug="harmonic_butterfly",
        description="Harmonic Butterfly pattern (Scott Carney): five swing points X-A-B-C-D whose leg ratios fall in the Butterfly bands (B 0.736-0.836 of XA, C 0.332-0.936 of AB, D 1.222-1.668 of XA). Entry at D completion (reversal), exit on the opposite pattern plus ATR stop / trail.",
        source_name="Harmonic Butterfly pattern (Scott Carney)",
        source_url="https://www.ebc.com/forex/harmonic-patterns",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
