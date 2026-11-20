"""Adaptive MACD: registration + re-exports."""

from strategies.adaptive_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Adaptive MACD",
        slug="adaptive_macd",
        description="MACD (Gerald Appel) with Kaufman efficiency-ratio adaptive EMAs: fast EMA smoothing adapts over period range 2..12 and slow over 5..26 via ER over 10 bars; signal is a 9-bar EMA of the MACD line. Long on a MACD cross above signal, short on a cross below; exit on the opposite cross, plus the harness stop/trail.",
        source_name="Kaufman efficiency ratio (Trading Systems and Methods) + Appel MACD",
        source_url="https://en.wikipedia.org/wiki/MACD",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
