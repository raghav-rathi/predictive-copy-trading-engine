"""Dual Momentum: registration + re-exports."""

from strategies.dual_momentum import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dual Momentum",
        slug="dual_momentum",
        description="Gary Antonacci's Dual Momentum Investing (2014): absolute momentum (240-bar log return, the 1h adaptation of the 12-month lookback) plus relative momentum vs the equal-weight BTC/ETH/HYPE basket. Long the top-ranked coin only when its absolute momentum is positive; short the bottom-ranked coin only when its absolute momentum is negative; flat otherwise. Exit on rank flip or absolute momentum turning against the position.",
        source_name="Gary Antonacci — Dual Momentum Investing (2014)",
        source_url="https://www.optimalmomentum.com/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
