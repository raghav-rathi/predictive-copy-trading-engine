"""Stochastic RSI cross: registration + re-exports."""

from strategies.stochastic_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic RSI Cross",
        slug="stochastic_rsi",
        description="StochRSI(14,14,3,3) cross (Chande & Kroll): long on %K crossing above %D out of oversold (prior %K < 20), short on %K crossing below %D out of overbought (prior %K > 80); exit on the opposite cross or %K crossing the far 80/20 level, plus the harness stop/trail.",
        source_name="StochRSI cross (Chande & Kroll, Stocks & Commodities 05/1993; The New Technical Trader 1994)",
        source_url="https://doc.stocksharp.com/en/api-examples/0025_Stochastic_RSI_Cross",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
