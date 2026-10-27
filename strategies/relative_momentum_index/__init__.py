"""Relative Momentum Index: registration + re-exports."""

from strategies.relative_momentum_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Relative Momentum Index",
        slug="relative_momentum_index",
        description=(
            "Roger Altman RMI(20,5): Wilder-smoothed gains/losses measured close-vs-close-5-bars-ago instead of consecutive closes; long on a cross above 50, short on a cross below 50."
        ),
        source_name="Roger Altman Relative Momentum Index (Technical Analysis of Stocks & Commodities, Feb 1993)",
        source_url="https://patternswizard.com/relative-momentum-index/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
