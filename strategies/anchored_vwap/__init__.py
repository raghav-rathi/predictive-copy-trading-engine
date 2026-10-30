"""Anchored VWAP: registration + re-exports."""

from strategies.anchored_vwap import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Anchored VWAP",
        slug="anchored_vwap",
        description=(
            "Brian Shannon anchored VWAP: VWAP reset at the most "
            "recent confirmed 20-bar swing-high and swing-low "
            "pivots (10 bars each side, activated 10 bars after "
            "the pivot so the series stays causal). Long on a "
            "close crossing above the swing-low AVWAP while it "
            "rises vs 5 bars ago; short on the mirror cross "
            "below the falling swing-high AVWAP. Exit on the "
            "opposite cross of the same AVWAP. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Anchored VWAP (Brian Shannon; Investopedia anchored VWAP)",
        source_url="https://www.investopedia.com/terms/a/anchored-vwap.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
