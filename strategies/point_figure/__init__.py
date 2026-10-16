"""Point & Figure engine: registration + re-exports."""

from strategies.point_figure import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Point & Figure 3-box reversal breakout",
        slug="point_figure",
        description=(
            "Classic P&F: box = 0.5xATR(14), columns built causally from "
            "closes, 3-box reversals. Entries on double-top breaks (X "
            "column top >= 1 box above prior X top) and double-bottom "
            "breaks; exits on the opposite breakout. 2xATR stop, 96-bar "
            "max hold."
        ),
        source_name="Point & Figure 3-box reversal (Dorsey/Wheeler)",
        source_url="https://www.globalbankingandfinance.com/understanding-point-and-figure-charting/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
