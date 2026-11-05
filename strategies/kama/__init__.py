"""Kaufman's Adaptive Moving Average: registration + re-exports."""

from strategies.kama import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kaufman's Adaptive Moving Average",
        slug="kama",
        description="Kaufman's Adaptive Moving Average KAMA(10,2,30): long when close crosses above KAMA and KAMA is rising; short when close crosses below KAMA and KAMA is falling; exit on the opposite cross.",
        source_name="Kaufman's Adaptive Moving Average (Perry Kaufman, 1995)",
        source_url="https://corporatefinanceinstitute.com/resources/capital_markets/kaufmans-adaptive-moving-average-kama/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
