"""Renko trend engine: registration + re-exports."""

from strategies.renko_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Renko brick-trend (renko)",
        slug="renko_trend",
        description=(
            "0.5xATR renko bricks from closes; entries on brick-direction "
            "reversals; exits on the opposite reversal; 2xATR stop, "
            "200-bar max hold."
        ),
        source_name="Renko chart mechanics — FasterCapital",
        source_url="https://fastercapital.com/topics/how-renko-charts-analyze-price-movements.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
