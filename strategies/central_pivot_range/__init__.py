"""Central Pivot Range: registration + re-exports."""

from strategies.central_pivot_range import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Central Pivot Range",
        slug="central_pivot_range",
        description=(
            "Frank Ochoa's Central Pivot Range from the prior UTC day: Pivot = (H+L+C)/3, BC = (H+L)/2, TC = 2*Pivot - BC. Long on a close crossing above TC, short below BC, exit back through the Pivot. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Central Pivot Range (Frank Ochoa)",
        source_url="https://www.stockmaniacs.net/central-pivot-range/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
