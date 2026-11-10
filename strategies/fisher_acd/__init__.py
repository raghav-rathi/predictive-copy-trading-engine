"""Mark Fisher ACD opening-range system: registration + re-exports."""

from strategies.fisher_acd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fisher ACD Opening Range",
        slug="fisher_acd",
        description="Mark Fisher ACD: the first 1h bar of each UTC day sets the opening range; long on a close crossing above OR high + 0.5 ATR with close above the previous day's pivot, short on the mirror image. Exit on a close back through the OR edge (B point); a close beyond the far C level (OR edge +/- 1.5 ATR) reverses the trade.",
        source_name='Mark Fisher — "The Logical Trader" (ACD)',
        source_url="https://www.investopedia.com/articles/technical/04/032404.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
