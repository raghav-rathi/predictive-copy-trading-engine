"""Breakout-retest (throwback) strategy: registration + re-exports."""

from strategies.breakout_retest import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Breakout-Retest Throwback",
        slug="breakout_retest",
        description=(
            "Breakout-retest / throwback (polarity principle): old "
            "resistance becomes new support. LONG: close crosses above "
            "the prior 20-bar high; enter on a clean retest within 20 "
            "bars (wick touches level + 0.1xATR, close back above the "
            "line); a close below level - 0.5xATR cancels the setup "
            "and exits the position. SHORT mirrors. 1.0xATR stop, "
            "2.0xATR measured-move target, 96-bar max hold."
        ),
        source_name="Breakout-retest (polarity principle)",
        source_url="https://agentictrading.info/learn/what-is-a-breakout-retest.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
