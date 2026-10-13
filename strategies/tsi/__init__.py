"""TSI engine: registration + re-exports."""

from strategies.tsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="True Strength Index (Blau)",
        slug="tsi",
        description=(
            "Blau's TSI(25,13) crossing its 7-period signal line for "
            "entries/exits, zero-line gate for mean-reversion flavor, "
            "optional +/-25 exhaustion exits; 2.5xATR stop, 120-bar max hold."
        ),
        source_name="William Blau, True Strength Index (1991)",
        source_url="https://en.wikipedia.org/wiki/True_strength_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
