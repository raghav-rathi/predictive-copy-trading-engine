"""Ehlers MESA Adaptive Moving Average crossover: registration + re-exports."""

from strategies.mesa_adaptive_ma import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MESA Adaptive Moving Average Crossover",
        slug="mesa_adaptive_ma",
        description="Ehlers MAMA/FAMA: Hilbert-transform phase rate drives an adaptive EMA alpha clamped to [0.05, 0.5]; FAMA follows MAMA at half alpha. Long on MAMA crossing above FAMA, short on cross below, exit on the opposite cross.",
        source_name="John F. Ehlers — Rocket Science for Traders (MAMA)",
        source_url="https://mesasoftware.com/papers/MAMA.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
