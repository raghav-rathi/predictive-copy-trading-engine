"""Fibonacci retracement: registration + re-exports."""

from strategies.fibonacci_retracement import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fibonacci Retracement",
        slug="fibonacci_retracement",
        description="Fibonacci retracement pullback (golden zone) on 5-bar fractal pivots: an impulse leg A->B of >= 1.0x ATR(14) defines the 38.2%-61.8% retracement zone; in an uptrend enter long on the close of the first green candle that closes in or above the zone after the first touch, exit at a close >= B (the old high) or below A (invalidation); short mirror in downtrends.",
        source_name="Fibonacci retracement pullback (TradingWalk)",
        source_url="https://tradingwalk.com/fibonacci-tips",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
