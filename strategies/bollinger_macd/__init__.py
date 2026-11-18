"""Bollinger MACD: registration + re-exports."""

from strategies.bollinger_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger MACD",
        slug="bollinger_macd",
        description="Bollinger(20, 2.0) band tag + MACD(12,26,9) cross: long on a MACD cross above signal with the low touching the lower band in the last 3 bars, short on the mirror; exit on the opposite MACD cross or reaching the opposite band, plus the harness stop/trail.",
        source_name="Bollinger Bands MACD Ultimate Combo Strategy (Stocks365)",
        source_url="https://www.stocks365.com/blog/bollinger-bands-macd-ultimate-combo-strategy-1139",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
