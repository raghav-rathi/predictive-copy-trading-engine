"""GMMA engine: registration + re-exports."""

from strategies.gmma import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="GMMA (Guppy multiple moving averages)",
        slug="gmma",
        description=(
            "12-EMA group crossover: buy when all short EMAs (3-15) cross "
            "above all long EMAs (30-60); exit on recross."
        ),
        source_name="GMMA (Daryl Guppy, Trend Trading) — BabyPips guide",
        source_url="http://babypips.com/learn/forex/guppy-multiple-moving-average",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
