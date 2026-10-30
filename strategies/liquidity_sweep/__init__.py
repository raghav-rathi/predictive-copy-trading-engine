"""Liquidity sweep: registration + re-exports."""

from strategies.liquidity_sweep import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Liquidity Sweep",
        slug="liquidity_sweep",
        description=(
            "Liquidity sweep + reclaim (Smart Money concept): "
            "a bar whose low wicks below the prior 20-bar swing "
            "low (or high above the prior 20-bar swing high) "
            "but closes back inside the range. Long on a "
            "reclaimed low sweep on the sweep bar or the next "
            "bar; short mirrored. Exit on the opposite sweep "
            "signal or the risk layer's trail. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Trading Liquidity Sweeps Like a Pro (International Trading Institute)",
        source_url="https://internationaltradinginstitute.com/blog/liquidity-sweeps-entry-exit-strategies/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
