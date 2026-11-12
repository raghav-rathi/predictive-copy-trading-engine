"""Linear Regression Channel: registration + re-exports."""

from strategies.regression_channel import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Linear Regression Channel",
        slug="regression_channel",
        description="Linear regression channel mean reversion: OLS line over 100 bars with bands at +/- 2.0 stddev of residuals; long when the close crosses back above the lower band, short when it crosses back below the upper band; exit at the regression midline.",
        source_name="Linear Regression Channel (Technical Analysis Pro) — mean reversion within the channel, target the center line",
        source_url="https://www.technical-analysis-pro.com/indicators-linear-regression-channel/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
