"""Gann swing engine: registration + re-exports."""

from strategies.gann_swing import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gann swing chart (1-bar / 3-bar) pullback entries",
        slug="gann_swing",
        description=(
            "Gann swing charts: 1-bar minor swing (higher highs+lows = "
            "up, lower = down, inside/outside bars hold) and 3-bar main "
            "trend (flip on a 3-bar high/low break). Entries on the "
            "1-bar swing turning back with the main trend (pullback "
            "timing); exits on main-trend flip. 2xATR stop, 96-bar max "
            "hold."
        ),
        source_name="Gann swing chart system (1-bar/3-bar)",
        source_url="https://github.com/passiontrader/geometric-trading-engine/blob/HEAD/Gann%20Market%20Geometry%20Rulebook%20Part%202.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
