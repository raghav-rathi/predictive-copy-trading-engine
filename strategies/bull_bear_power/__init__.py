"""Bull Power / Bear Power: registration + re-exports."""

from strategies.bull_bear_power import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bull Bear Power",
        slug="bull_bear_power",
        description="Alexander Elder's Elder-Ray index (Trading for a Living, 1993): Bull Power = high - EMA(13), Bear Power = low - EMA(13). Long when Bear Power turns up while still below zero and Bull Power is above zero; short when Bull Power turns down while still above zero and Bear Power is below zero; exit on the opposite turn, with the harness stop/trail as the exit mechanism.",
        source_name="Alexander Elder — Bull Power / Bear Power (Elder-Ray), Trading for a Living (1993)",
        source_url="https://piprider.com/bulls-and-bears-power-indicators/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
