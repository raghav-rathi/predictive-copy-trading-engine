"""Donchian ADX: registration + re-exports."""

from strategies.donchian_adx import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian ADX",
        slug="donchian_adx",
        description="Donchian 20 breakout with a Wilder ADX(14) > 25 trend filter: long on a breakout up with ADX > 25, short on a breakout down with ADX > 25; exit when ADX falls below 20 or on the opposite breakout.",
        source_name="Donchian Channels + Wilder ADX(14)",
        source_url="https://learn.tradelabsai.com/indicators/donchian-channels/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
