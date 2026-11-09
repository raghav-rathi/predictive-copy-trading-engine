"""Ichimoku Kumo twist: registration + re-exports."""

from strategies.kumo_twist import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ichimoku Kumo Twist",
        slug="kumo_twist",
        description="Ichimoku cloud twist: long when Senkou Span A crosses above Senkou Span B, short on a cross below, exit on the opposite twist. Spans are evaluated causally from data through bar i, WITHOUT the standard 26-bar forward displacement — the twist is the current cloud changing colour, not the projected cloud.",
        source_name="BabyPips — Ichimoku Kinko Hyo",
        source_url="https://www.babypips.com/learn/forex/ichimoku-kinko-hyo",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
