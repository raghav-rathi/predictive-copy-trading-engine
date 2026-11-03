"""Fibonacci Pivots: registration + re-exports."""

from strategies.fibonacci_pivots import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fibonacci Pivots",
        slug="fibonacci_pivots",
        description=(
            "Fibonacci pivot points on 1h bars: levels from the prior completed 24-bar block (pivot = (H+L+C)/3; R1 = P + 0.382*(H-L), S1 = P - 0.382*(H-L)). Long on close cross above R1, short on cross below S1; exits on cross back through the pivot. Levels are fixed within a block — no intraday repainting."
        ),
        source_name="Fibonacci pivot points",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:pivot_points",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
