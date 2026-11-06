"""Stochastic Divergence: registration + re-exports."""

from strategies.stochastic_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic Divergence",
        slug="stochastic_divergence",
        description="George Lane slow stochastic (14,3,3) regular and hidden divergence on 5-bar swing pivots: regular divergence signals reversals, hidden divergence signals trend continuation, confirmed 2 bars after the pivot.",
        source_name="George Lane stochastic + regular/hidden divergence",
        source_url="https://cryptensive.com/blog/trading-divergences-regular-and-hidden/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
