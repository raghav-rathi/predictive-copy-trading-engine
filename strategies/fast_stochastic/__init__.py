"""Lane Fast Stochastic: registration + re-exports."""

from strategies.fast_stochastic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Lane Fast Stochastic",
        slug="fast_stochastic",
        description=(
            "Lane Fast Stochastic %K(14)/%D(3): long on %K crossing above %D while %D is oversold (<20), short on crossing below %D while %D is overbought (>80)."
        ),
        source_name="George Lane Fast Stochastic (Technical Analysis of Stocks & Commodities)",
        source_url="https://www.investopedia.com/terms/s/stochasticoscillator.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
