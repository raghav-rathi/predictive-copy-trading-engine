"""MACD zero-line cross: registration + re-exports."""

from strategies.macd_zero_line import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Zero-Line Cross",
        slug="macd_zero_line",
        description="MACD(12, 26, 9) zero-line cross system: the MACD line is EMA(12) minus EMA(26) of close; long when the line crosses above zero, short when it crosses below zero, and exit on the reverse zero cross. A pure momentum regime flip — the fast EMA overtaking the slow EMA.",
        source_name="MACD indicator strategy (qtfx.dev)",
        source_url="https://www.qtfx.dev/en/indicators/macd-indicator-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
