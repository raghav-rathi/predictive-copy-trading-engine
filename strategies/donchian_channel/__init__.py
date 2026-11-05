"""Donchian channel: registration + re-exports."""

from strategies.donchian_channel import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian Channel",
        slug="donchian_channel",
        description="Donchian 20-bar breakout: long on a close above the prior 20-bar highest high, short on a close below the prior 20-bar lowest low; exit on a close back through the channel midline.",
        source_name="Donchian Channels",
        source_url="https://learn.tradelabsai.com/indicators/donchian-channels/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
