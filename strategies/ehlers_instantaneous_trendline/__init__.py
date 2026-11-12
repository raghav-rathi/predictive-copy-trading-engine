"""Ehlers Instantaneous Trendline: registration + re-exports."""

from strategies.ehlers_instantaneous_trendline import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Instantaneous Trendline",
        slug="ehlers_instantaneous_trendline",
        description="John F. Ehlers' Instantaneous Trendline (Cybernetic Analysis for Stocks and Futures, 2004), alpha 0.07: long when the close crosses above the near-zero-lag trendline, short when it crosses below; exit on the opposite cross, with the harness stop/trail as the exit mechanism.",
        source_name="John F. Ehlers — Instantaneous Trendline, Cybernetic Analysis for Stocks and Futures (2004)",
        source_url="https://www.fmz.com/lang/en/strategy/436000",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
