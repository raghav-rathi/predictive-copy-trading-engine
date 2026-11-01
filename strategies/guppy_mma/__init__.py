"""Guppy MMA: registration + re-exports."""

from strategies.guppy_mma import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Guppy MMA",
        slug="guppy_mma",
        description=(
            "Daryl Guppy's Multiple Moving Average ribbon: the mean of six short-term EMAs (3/5/8/10/12/15) crossing the mean of six long-term EMAs (30/35/40/45/50/60) signals trend change; exit on the opposite cross. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Guppy Multiple Moving Average (Daryl Guppy)",
        source_url="https://capital.com/en-int/learn/technical-analysis/gmma-indicator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
