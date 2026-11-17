"""Heikin Ashi + MACD momentum filter: registration + re-exports."""

from strategies.heikin_ashi_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Heikin Ashi + MACD Momentum Filter",
        slug="heikin_ashi_macd",
        description="Heikin Ashi candles with MACD(12, 26, 9) on the HA close: long when the MACD histogram crosses above 0 on a bullish HA candle (HA close > HA open), short when it crosses below 0 on a bearish HA candle. Exit on the opposite histogram zero-cross, plus the harness stop/trail.",
        source_name="TradingView \"Heikin Ashi + MACD Momentum Filter\" by Raisontgh",
        source_url="https://tw.tradingview.com/script/uXNlGkhO-Heikin-Ashi-MACD-Momentum-Filter/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
