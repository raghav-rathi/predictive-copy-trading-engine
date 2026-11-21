"""Accumulation/Distribution Line: registration + re-exports."""

from strategies.accumulation_distribution import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Accumulation/Distribution Line",
        slug="accumulation_distribution",
        description="Marc Chaikin A/D line: money flow multiplier ((C-L)-(H-C))/(H-L) times volume, cumulated; signal line SMA(20) of AD. Long on AD crossing up through its SMA(20), short on a cross down; exit on the opposite cross, plus the harness stop/trail.",
        source_name="Marc Chaikin, Accumulation/Distribution Line / TrendSpider",
        source_url="https://trendspider.com/learning-center/accumulation-distribution-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
