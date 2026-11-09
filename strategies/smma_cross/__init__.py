"""Wilder's SMMA crossover: registration + re-exports."""

from strategies.smma_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SMMA Crossover",
        slug="smma_cross",
        description="Wilder's Smoothed MA crossover: SMMA(9) vs SMMA(21), SMA-seeded with alpha = 1/n recursion. Long on cross up, short on cross down, exit on the opposite cross.",
        source_name="J. Welles Wilder — New Concepts in Technical Trading Systems (1978)",
        source_url="https://en.wikipedia.org/wiki/Moving_average#Smoothed_moving_average",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
