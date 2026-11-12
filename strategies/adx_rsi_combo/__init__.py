"""ADX + RSI Combo: registration + re-exports."""

from strategies.adx_rsi_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ADX + RSI Combo",
        slug="adx_rsi_combo",
        description="ADX(14) trend filter + RSI(14) momentum: long when RSI crosses above 30 with ADX > 25, short when RSI crosses below 70 with ADX > 25; exit long when RSI crosses back below 50, exit short when RSI crosses back above 50.",
        source_name="ADX and RSI Trading Strategies (OpoFinance) — ADX above 25 trend filter with RSI 30/70 levels",
        source_url="https://blog.opofinance.com/en/adx-and-rsi-trading-strategies/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
