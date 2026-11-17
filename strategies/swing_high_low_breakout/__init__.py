"""Swing-structure breakout: registration + re-exports."""

from strategies.swing_high_low_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Swing High Low Breakout",
        slug="swing_high_low_breakout",
        description="Swing-structure breakout on 5-bar pivots (a swing high is a high strictly greater than the 2 bars on each side, swing low mirror; pivots recorded at their confirmation bar, center + 2). Long on a close above the last swing high with the last two swing lows ascending; short on a close below the last swing low with the last two swing highs descending. Exit on the opposite structure break, plus the harness stop/trail. Pure structure breakout — entry fires on the break itself, not on a pullback.",
        source_name="Swing-structure / market-structure breakout (5-bar pivots)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
