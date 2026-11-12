"""MACD Histogram: registration + re-exports."""

from strategies.macd_histogram import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Histogram",
        slug="macd_histogram",
        description="Gerald Appel's MACD (1970s), 12/26/9 defaults: long when the MACD histogram crosses above zero (MACD crosses above its 9-period signal line), short when it crosses below zero; exit on the opposite cross, with the harness stop/trail as the exit mechanism.",
        source_name="Gerald Appel — MACD (Moving Average Convergence Divergence), 12/26/9",
        source_url="https://www.cmelitegroup.com/knowledge-hub/macd-indicator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
