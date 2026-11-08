"""Rising/falling three methods: registration + re-exports."""

from strategies.rising_three_methods import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Rising Three Methods",
        slug="rising_three_methods",
        description="Rising/falling three methods: a long bar-1 candle (body >= 1.0x ATR(14)) in the trend direction, three small counter-trend candles fully inside bar 1's range, then a bar-5 candle closing beyond bar 1's high/low; enter on bar 5's close, exit on a close beyond bar 1's opposite extreme.",
        source_name="Dipak7 — Bullish & Bearish Candlestick Patterns (2026)",
        source_url="https://dipak7.com.np/bullish-bearish-candlestick-patterns/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
