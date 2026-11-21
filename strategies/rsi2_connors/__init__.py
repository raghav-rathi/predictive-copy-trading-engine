"""Connors RSI(2): registration + re-exports."""

from strategies.rsi2_connors import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Connors RSI(2)",
        slug="rsi2_connors",
        description="Larry Connors' Connors RSI: mean of RSI(3) of close, RSI(3) of the up/down streak series, and the percentile rank of the 1-bar ROC over the trailing 100 bars. Long on a cross below 10, short on a cross above 90; exit on a cross of 50 the other way; plus the harness stop/trail.",
        source_name="Larry Connors, Short Term Trading Strategies That Work (2008); Connors RSI",
        source_url="https://therighttrader.com/learn/indicators/connors-rsi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
