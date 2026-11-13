"""ICT Power of Three / AMD: registration + re-exports."""

from strategies.ict_power_of_three import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ICT Power of Three",
        slug="ict_power_of_three",
        description="ICT Power of Three / Accumulation-Manipulation-Distribution (Michael J. Huddleston), adapted to 24/7 crypto on UTC days. Accumulation is the range of the first 8 hours of the UTC day (00:00-08:00 UTC); manipulation is a sweep of the range low/high by >= 0.25 x ATR(14) during 08:00-16:00 UTC; distribution is price closing back through the range in the opposite direction of the sweep during 16:00-24:00 UTC — long after a low sweep plus a reclaim above the range low, short after a high sweep plus a reclaim below the range high. One trade per day maximum; exit at the end of the UTC day, with the harness stop/trail as the exit mechanism.",
        source_name="ICT Power of Three / AMD (Michael J. Huddleston)",
        source_url="https://velotrade.com/blog/accumulation-manipulation-distribution",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
