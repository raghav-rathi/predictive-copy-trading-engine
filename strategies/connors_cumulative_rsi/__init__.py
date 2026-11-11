"""Connors Cumulative RSI: registration + re-exports."""

from strategies.connors_cumulative_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Connors Cumulative RSI",
        slug="connors_cumulative_rsi",
        description="Larry Connors' Cumulative RSI: Wilder RSI(2), cumulated as the running sum of (RSI(2) - 50) with no reset. Long when cum_rsi crosses back above -100, short when it crosses back below +100; exits on the cum_rsi cross of 0. Mean-reversion on the cumulative oscillator.",
        source_name="Larry Connors & Cesar Alvarez — Cumulative RSI (High Probability ETF Trading, 2009)",
        source_url="https://trader.autochartist.com/cumulative-rsi-system/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
