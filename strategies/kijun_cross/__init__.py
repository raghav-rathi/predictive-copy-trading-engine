"""Kijun Cross: registration + re-exports."""

from strategies.kijun_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kijun Cross",
        slug="kijun_cross",
        description=(
            "Ichimoku Kijun-sen (26-bar midpoint) cross: long when close crosses above Kijun, short below, exit on the opposite cross — the baseline trend line alone, without the cloud."
        ),
        source_name="Ichimoku Kijun-sen (Goichi Hosoda)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:ichimoku_cloud",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
