"""Stochastic %K/%D cross + MACD histogram: registration + re-exports."""

from strategies.stochastic_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic %K/%D Cross + MACD Histogram",
        slug="stochastic_macd",
        description="Stochastic(14,3,3) %K/%D cross + MACD(12,26,9) histogram agreement: long on %K crossing above %D while %K < 30 with MACD histogram > 0; short on %K crossing below %D while %K > 70 with histogram < 0. Exit on the opposite %K/%D cross or a histogram sign flip against; plus the harness stop/trail.",
        source_name="George Lane stochastic; Gerald Appel MACD",
        source_url="https://www.investopedia.com/terms/s/stochasticoscillator.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
