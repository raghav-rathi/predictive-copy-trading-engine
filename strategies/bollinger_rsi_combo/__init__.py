"""Bollinger + short-period RSI mean reversion: registration + re-exports."""

from strategies.bollinger_rsi_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger + RSI Mean Reversion",
        slug="bollinger_rsi_combo",
        description="Bollinger Bands (20, 2) + RSI(2): enter long on the recovery close back inside the lower band after a bar closed below it with RSI(2) under 10; mirror for shorts. Exit at the middle band or on an opposite RSI(2) extreme.",
        source_name="TradingCompendium — Mean Reversion Strategy: RSI + Bollinger Bands Rules",
        source_url="https://tradingcompendium.com/en/trading-strategies/mean-reversion-strategy-rsi-bollinger",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
