"""Tweezer top/bottom reversal: registration + re-exports."""

from strategies.tweezer_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Tweezer Reversal",
        slug="tweezer_reversal",
        description="Tweezer bottom/top reversal: after a 5-bar trend vs SMA(50), two consecutive bars with near-equal lows/highs (within 0.1x ATR(14)) and opposite candles, second candle closing past the first candle's midpoint; enter on the second bar's close, exit on a close beyond the tweezer extreme.",
        source_name="Finviro — Japanese Candlestick Pattern Encyclopedia",
        source_url="https://finviro.com/en/academy/patterns",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
