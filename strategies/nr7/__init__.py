"""NR7 engine: registration + re-exports."""

from strategies.nr7 import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="NR7 narrow-range breakout (Crabel)",
        slug="nr7",
        description=(
            "Narrowest range of 7 bars flags compression; trade the break "
            "of the NR7 bar's high/low, stop at the opposite extreme; "
            "1.5xATR stop, 24-bar max hold."
        ),
        source_name="NR7 breakout (Toby Crabel) — strategyvisualizer",
        source_url="https://github.com/timcodes/strategyvisualizer/blob/HEAD/strategy-library/038-nr7-breakout.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
