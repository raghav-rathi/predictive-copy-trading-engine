"""Engulfing reversal pattern: registration + re-exports."""

from strategies.engulfing_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Engulfing Pattern Reversal",
        slug="engulfing_pattern",
        description=(
            "Classic two-candle reversal: a bullish engulfing (green body "
            "fully covering the prior red body) buys the dip only when the "
            "close is above EMA(20); a bearish engulfing (red body fully "
            "covering the prior green body) sells the rally only when the "
            "close is below EMA(20). Exits on the opposite engulfing; "
            "1.5xATR stop, 2xATR chandelier trail, 48-bar max hold. "
            "Act on the closed engulfing candle, never intrabar."
        ),
        source_name="Halley Tech — Reversal Candlestick Patterns",
        source_url="https://halleytech.substack.com/p/reversal-candlestick-patterns",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
