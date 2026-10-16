"""Minervini Trend Template engine: registration + re-exports."""

from strategies.minervini_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Minervini Trend Template (long-only stage-2)",
        slug="minervini_trend",
        description=(
            "Minervini's 8-criterion trend template on 1h bars (24 bars/day): "
            "price and SMA(50d) above SMA(150d)/SMA(200d), 200d rising vs "
            "30d ago, >=30% above the 52wk low, within 25% of the 52wk high. "
            "Entry on the false->true template flip; exit on template "
            "breakdown. LONG ONLY. 2xATR stop, 3xATR trail, 720-bar max hold."
        ),
        source_name="Mark Minervini trading strategy — financialtechwiz",
        source_url="https://www.financialtechwiz.com/post/mark-minervini-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
