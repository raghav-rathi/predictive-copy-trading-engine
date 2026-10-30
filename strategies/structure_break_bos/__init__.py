"""Structure-break BOS: registration + re-exports."""

from strategies.structure_break_bos import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Structure Break (BOS)",
        slug="structure_break_bos",
        description=(
            "Market-structure Break of Structure / Change of "
            "Character from 5-bar swing pivots, confirmed only "
            "after the 2 bars to their right have closed. Long "
            "on a close above the prior swing high while the "
            "last structure break was also upward (BOS "
            "continuation: a higher high confirming the "
            "uptrend leg); short mirrored. Exit on the "
            "opposite structure break. 2xATR stop, 2.5xATR "
            "trail, 120-bar max hold."
        ),
        source_name="Break of Structure (BOS) vs CHoCH Explained (Velotrade)",
        source_url="https://velotrade.com/blog/break-of-structure",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
