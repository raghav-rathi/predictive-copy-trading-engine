"""Donchian Channel Breakout: registration + re-exports."""

from strategies.donchian_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian Channel Breakout",
        slug="donchian_breakout",
        description="Richard Dennis / Turtle Traders Donchian(20) breakout: long when the close breaks above the highest high of the prior 20 bars (transition only), short when it breaks below the lowest low of the prior 20 bars; exits on the opposite 20-bar extreme or the Turtle 10-bar exit, plus the harness stop/trail.",
        source_name="Richard Dennis / Turtle Traders Donchian channels (PatternsWizard)",
        source_url="https://patternswizard.com/donchian-channel/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
