"""Schaff Trend Cycle engine: registration + re-exports."""

from strategies.schaff_trend_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Schaff Trend Cycle",
        slug="schaff_trend_cycle",
        description=(
            "Schaff Trend Cycle: MACD(12,26) stochastically normalized over "
            "50 bars, double-smoothed (23,50) then EMA10, 0-100. Long on "
            "cross up through 25, short on cross down through 75; opposing "
            "cross exits. 2xATR stop."
        ),
        source_name="Doug Schaff, Schaff Trend Cycle",
        source_url="https://www.forex.in.rs/trend-cycle/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
