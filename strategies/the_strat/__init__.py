"""The Strat engine: registration + re-exports."""

from strategies.the_strat import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="The Strat",
        slug="the_strat",
        description=(
            "Rob Smith's The Strat: bar classification (1 inside, "
            "2U/2D single-side break, 3 outside) with 2-1-2, 3-1-2 "
            "and 2-2 reversal setups plus 2-1-2 continuation, gated "
            "by full-time-frame continuity (daily AND weekly green "
            "for longs, both red for shorts); opposite setup exits; "
            "2xATR stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="Rob Smith — The Strat (LuxAlgo concept library)",
        source_url="https://www.luxalgo.com/library/concept/the-strat/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
