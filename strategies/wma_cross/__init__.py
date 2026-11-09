"""WMA crossover: registration + re-exports."""

from strategies.wma_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="WMA Crossover",
        slug="wma_cross",
        description="Linearly weighted moving average crossover: WMA(9) vs WMA(21), newest close weighted most. Long on cross up, short on cross down, exit on the opposite cross.",
        source_name="Investopedia — Weighted Moving Average (WMA)",
        source_url="https://www.investopedia.com/terms/w/weightedmovingaverage.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
