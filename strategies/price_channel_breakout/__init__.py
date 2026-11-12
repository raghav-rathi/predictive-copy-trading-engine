"""Price Channel Breakout: registration + re-exports."""

from strategies.price_channel_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Price Channel Breakout",
        slug="price_channel_breakout",
        description="Richard Donchian's price channel (1960s): long when the close breaks above the highest high of the prior 30 bars, short when it breaks below the lowest low of the prior 30 bars; exit long on a close back below the channel midline, exit short on a close back above it, with the harness stop/trail as the exit mechanism.",
        source_name="Richard Donchian — Donchian Channel Breakout (Turtle Trading system)",
        source_url="https://www.fintechvps.com/blog/donchian-channel-breakout",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
