"""Inside-bar breakout engine: registration + re-exports."""

from strategies.inside_bar import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Inside-bar breakout (classic price action)",
        slug="inside_bar",
        description=(
            "Inside bar with EMA50 trend bias arms a 2-bar breakout watch; "
            "entries on mother-bar extreme breaks; 2xATR stop, 4xATR "
            "target, 48-bar max hold."
        ),
        source_name="Inside bar breakout (classic price action)",
        source_url="https://github.com/timcodes/strategyvisualizer/blob/HEAD/strategy-library/039-inside-bar-breakout.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
