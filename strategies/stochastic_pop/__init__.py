"""Stochastic Pop: registration + re-exports."""

from strategies.stochastic_pop import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic Pop",
        slug="stochastic_pop",
        description=(
            "Linda Raschke Stochastic Pop: fast %K(14) crosses above "
            "80 while price breaks above the prior 20-bar high (long), "
            "or crosses below 20 with a prior 20-bar-low breakdown "
            "(short). A breakout with the oscillator already pinned "
            "at an extreme is continuation, not a fade. Distinct "
            "from stoch_hook (slow-K trigger cross, no breakout). "
            "Exit when %K leaves the extreme zone. 1.5xATR stop, "
            "2xATR trail, 3xATR target, 72-bar max hold."
        ),
        source_name="Stochastic Pop (Linda Raschke, Street Smarts)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-oscillators/stochastic-oscillator-fast-slow-and-full",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
