"""Initial Balance breakout (Market Profile): registration + re-exports."""

from strategies.initial_balance_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Initial Balance Breakout",
        slug="initial_balance_breakout",
        description="Market Profile Initial Balance breakout: the IB is the high/low of the first 1h bar of each UTC day; trade the first closed-bar break of the IB high (long) or low (short), one trade per day, exit on reclaim of the broken level or at the 1x IB extension target.",
        source_name="J. Peter Steidlmayer — Market Profile (CBOT, 1980s)",
        source_url="https://www.loomiai.io/learn/initial-balance-breakout-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
