"""Ichimoku Cloud: registration + re-exports."""

from strategies.ichimoku_cloud import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ichimoku Cloud",
        slug="ichimoku_cloud",
        description="Ichimoku (Goichi Hosoda, 9/26/52): long on a Tenkan crossing above the Kijun while the close is above the cloud and the cloud ahead is green, with Chikou confirmation (current close above the close 26 bars ago); short mirror. Exit on a Tenkan/Kijun cross back or a close into the cloud.",
        source_name="Ichimoku Cloud",
        source_url="https://velotrade.com/blog/ichimoku-cloud",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
