"""Donchian Turtle Breakout (System 1): registration + re-exports."""

from strategies.base import StrategySpec
from strategies.donchian_turtle_breakout import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian Turtle Breakout (System 1)",
        slug="donchian_turtle_breakout",
        description=(
            "Original Turtle Traders System 1 (Dennis & Eckhardt, 1983): "
            "LONG on a close above the prior-20-bar Donchian high, SHORT "
            "on a close below the prior-20-bar low; exit LONG on a close "
            "below the prior-10-bar low, SHORT above the prior-10-bar "
            "high. 2xATR(20) stop, no trail/target, 336-bar max hold. "
            "System 1 only (no 55-day System 2); the Turtles' "
            "'skip a breakout if the previous one was a winner' rule is "
            "NOT implemented — a documented deviation."
        ),
        source_name="Curtis Faith, Way of the Turtle (2007) — Turtle trading (System 1)",
        source_url="https://en.wikipedia.org/wiki/Turtle_trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
