"""TRIX momentum-turn engine: registration + re-exports."""

from strategies.trix import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TRIX Momentum Turn",
        slug="trix",
        description=(
            "TRIX (Hutson): triple EMA(14) of close, trix = 100*pct "
            "change of EMA3, signal = EMA(trix, 9); long when TRIX crosses "
            "above its signal while still below zero, short on a cross "
            "below while still above zero; exits on the opposite cross; "
            "2xATR stop, 3xATR chandelier trail, 200-bar max hold."
        ),
        source_name="TRIX (Jack Hutson)",
        source_url="https://capital.com/en-eu/learn/technical-analysis/trix-indicator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
