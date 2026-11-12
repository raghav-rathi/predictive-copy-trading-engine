"""Donchian + RSI: registration + re-exports."""

from strategies.donchian_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian + RSI",
        slug="donchian_rsi",
        description="Richard Donchian's 20-bar channel breakout with RSI(14) confirmation: long when the close breaks above the prior 20-bar high with RSI > 55, short when it breaks below the prior 20-bar low with RSI < 45; exit on the opposite Donchian breakout.",
        source_name="Donchian Channel and RSI Strategy (IQ Option Wiki) — Richard Donchian's 20-period channel",
        source_url="https://iqoptionwiki.com/donchian-channel-and-rsi-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
