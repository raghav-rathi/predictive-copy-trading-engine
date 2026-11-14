"""Gaussian filter trend engine: registration + re-exports."""

from strategies.gaussian_filter_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gaussian Filter Trend",
        slug="gaussian_filter_trend",
        description=(
            "Gaussian filter trend (Ehlers, Rocket Science for Traders "
            "Ch. 15): 4-pole recursive Gaussian filters of close, "
            "periods 10 and 30, alpha = "
            "(1-sin(2*pi/period))/cos(2*pi/period); CORRECTION: with "
            "this alpha the period-30 filter is the FAST tracker and "
            "period-10 the slow baseline, so long when the period-30 "
            "filter crosses above the period-10 filter, short on a "
            "cross below; exits on the opposite cross; 2xATR stop, "
            "3xATR chandelier trail, 200-bar max hold."
        ),
        source_name="Gaussian Filter (John Ehlers, Rocket Science for Traders Ch. 15)",
        source_url="https://www.luxalgo.com/library/indicator/gaussian-filter/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
