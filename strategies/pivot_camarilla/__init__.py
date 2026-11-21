"""Camarilla Pivot Breakout: registration + re-exports."""

from strategies.pivot_camarilla import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Camarilla Pivot Breakout",
        slug="pivot_camarilla",
        description="Nick Scott Camarilla Equation (1989): R3 = prior-day close + (prior-day high - low) * 1.055, S3 = prior-day close - (high - low) * 1.055, levels from the prior completed UTC day only. Long on a close crossing above R3, short on a close crossing below S3; exit on a cross back through the level, plus the harness stop/trail.",
        source_name="Nick Scott, Camarilla Equation (1989) / BabyPips Camarilla Pivot Points",
        source_url="https://www.babypips.com/forexpedia/camarilla-pivot",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
