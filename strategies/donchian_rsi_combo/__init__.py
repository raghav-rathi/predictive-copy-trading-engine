"""Donchian RSI combo engine: registration + re-exports."""

from strategies.donchian_rsi_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian RSI Combo",
        slug="donchian_rsi_combo",
        description=(
            "Richard Donchian channel breakout + RSI filter: long on "
            "a close above the prior 20-bar Donchian high with RSI < "
            "70, short on a close below the prior 20-bar low with "
            "RSI > 30; Turtle exit on the 10-bar channel; 2xATR stop, "
            "3xATR trail, 120-bar max hold."
        ),
        source_name="Richard Donchian — Donchian channel (Wikipedia)",
        source_url="https://en.wikipedia.org/wiki/Donchian_channel",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
