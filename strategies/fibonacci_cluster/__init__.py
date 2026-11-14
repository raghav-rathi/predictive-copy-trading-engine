"""Fibonacci cluster engine: registration + re-exports."""

from strategies.fibonacci_cluster import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fibonacci Cluster",
        slug="fibonacci_cluster",
        description=(
            "Fibonacci confluence zones: ZigZag swings from 5-bar "
            "fractal pivots (2-bar confirmation, min 2% swing); "
            "38.2%/50%/61.8% retracements of the last 3 completed "
            "swings; a cluster is >= 2 levels from different swings "
            "within 0.5x ATR(14); long on a low touching a support "
            "cluster and closing back above it, short on a high "
            "touching a resistance cluster and closing back below "
            "it; exit on touch of the opposite cluster; 2xATR stop, "
            "3xATR chandelier trail, 200-bar max hold."
        ),
        source_name="Fibonacci confluence / clusters",
        source_url="https://www.fxfoundations.com/learn/technical-analysis/fibonacci",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
