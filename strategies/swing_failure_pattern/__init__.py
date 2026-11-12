"""Swing Failure Pattern: registration + re-exports."""

from strategies.swing_failure_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Swing Failure Pattern",
        slug="swing_failure_pattern",
        description="Larry Williams swing-failure / false-breakout pattern: a new 20-bar high that closes back below the swing high within 3 bars is a short; a new 20-bar low that closes back above the swing low within 3 bars is a long. Exit on the opposite failure signal, with the harness stop/trail as the exit mechanism.",
        source_name="Larry Williams — Swing Failure Pattern / false breakout",
        source_url="https://www.osl.com/hk-en/academy/article/what-is-the-swing-failure-pattern-and-how-to-use-it-in-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
