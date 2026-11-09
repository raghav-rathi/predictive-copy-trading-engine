"""Linear regression slope: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.linear_regression_slope import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Linear Regression Slope",
        slug="linear_regression_slope",
        description="LinReg(20) OLS slope of close, normalized by price: enter long when the slope turns positive with R^2 >= 0.5; mirror for shorts. Exit on a slope sign flip or R^2 falling below 0.3.",
        source_name="LuxAlgo — R-squared Trend Fit",
        source_url="https://www.luxalgo.com/library/concept/r-squared-trend-fit/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
