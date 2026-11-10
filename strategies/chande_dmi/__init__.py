"""Chande Dynamic Momentum Index: registration + re-exports."""

from strategies.chande_dmi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande Dynamic Momentum Index",
        slug="chande_dmi",
        description="Chande & Kroll's Dynamic Momentum Index: a variable-length RSI whose lookback TD = clamp(round(14 / Vi), 5, 30) adapts to relative volatility Vi = stddev(close, 5) / SMA(stddev, 10). Long on DMI crossing up through 30, short on crossing down through 70, exit on the opposite extreme cross.",
        source_name="Tushar Chande & Stanley Kroll — The New Technical Trader (1994)",
        source_url="https://docs.wickra.org/Indicators/Indicator-DynamicMomentumIndex",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
