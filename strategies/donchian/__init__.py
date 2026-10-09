"""Donchian breakout engine: registration + re-exports."""

from strategies.donchian import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian Breakout (Turtle, ADX-filtered)",
        slug="donchian",
        description=(
            "20-bar Donchian breakout entries gated by ADX(14)>20 trend regime; "
            "10-bar channel exits; 2xATR stop with 3xATR chandelier trailing."
        ),
        source_name="The Original Turtle Trading Rules (Curtis Faith, public PDF)",
        source_url="https://www.metastock.com/Customer/Resources/TAAZ/?p=91",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
