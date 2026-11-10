"""Connors Double 7s mean-reversion system: registration + re-exports."""

from strategies.connors_double_sevens import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Connors Double 7s",
        slug="connors_double_sevens",
        description="Larry Connors & Cesar Alvarez Double 7s: long-only mean reversion on UTC-day closes. Long when the daily close is the lowest close of the last 7 days and above the 200-day SMA; exit when the daily close is the highest close of the last 7 days. No stop loss, no target — the 7-day-high close is the only exit.",
        source_name="Larry Connors & Cesar Alvarez — Short Term Trading Strategies That Work (Double 7s)",
        source_url="https://thealgobench.com/strategies/double-seven/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
