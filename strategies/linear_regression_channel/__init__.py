"""Linear regression channel: registration + re-exports."""

from strategies.linear_regression_channel import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Linear Regression Channel",
        slug="linear_regression_channel",
        description=(
            "Raff regression channel mean reversion on 1h bars: OLS "
            "fit of closes over a trailing 50-bar window, bands at "
            "mid +/- 2 residual std. Long on a close crossing below "
            "the lower band, short above the upper band, exit back "
            "across the midline. 2xATR stop, 2.5xATR trail, 120-bar "
            "max hold."
        ),
        source_name="Raff Regression Channel (Gilbert Raff)",
        source_url="https://www.interactivebrokers.eu/campus/glossary-terms/raff-channel-indicator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
