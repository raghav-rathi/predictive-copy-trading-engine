"""Swing Failure Pattern (SFP): registration + re-exports."""

from strategies.sfp import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Swing Failure Pattern",
        slug="sfp",
        description="Swing Failure Pattern: long when the low sweeps below the last confirmed swing low and the close reclaims it on a volume spike (>1.5x SMA20), short on the mirror sweep of a swing high; exit when the close fails back through the swept level or the opposite SFP prints, plus the harness stop/trail.",
        source_name="LuxAlgo Swing Failure Pattern; Thrive.fi Swing Failure Patterns",
        source_url="https://www.luxalgo.com/library/concept/swing-failure-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
