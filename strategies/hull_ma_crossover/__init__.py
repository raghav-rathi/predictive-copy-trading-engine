"""Hull MA crossover: registration + re-exports."""

from strategies.hull_ma_crossover import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hull MA Crossover",
        slug="hull_ma_crossover",
        description="Hull Moving Average crossover (Alan Hull, 2005): HMA(n) = WMA(2*WMA(n/2) - WMA(n), sqrt(n)). Long on HMA(16) crossing above HMA(32) with the fast HMA slope positive; short on a cross below with the slope negative; exit on the opposite cross. Note: Alan Hull himself warned against HMA crossovers (they reintroduce lag/whipsaw) — this is a test of the popular retail variant, not Hull's recommended slope method.",
        source_name="Hull Moving Average (Alan Hull)",
        source_url="https://capital.com/en-int/learn/technical-analysis/hull-moving-average",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
