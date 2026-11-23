"""Tillson T3 trend: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.t3_ma_trend import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Tillson T3 Trend",
        slug="t3_ma_trend",
        description=(
            "Tillson T3 trend (Tim Tillson, 1998): LONG when close is "
            "above T3(10, 0.7) with T3(10) rising and T3(10) above "
            "T3(30, 0.7); SHORT on the mirror. Exits on a close back "
            "through T3(10) or T3(10) turning against the position. "
            "Transition-only entries via a position state machine. "
            "T3 is a lag-reduced stack of six EMAs, not a new "
            "indicator family."
        ),
        source_name="Tim Tillson, Smoothing Techniques for More Accurate Signals (Technical Analysis of Stocks & Commodities, Jan 1998)",
        source_url="https://www.mesasoftware.com/papers/T3.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
