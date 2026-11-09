"""Chikou-span cross: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.chikou_span_cross import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chikou Span Cross",
        slug="chikou_span_cross",
        description="Ichimoku Chikou span: long when the close crosses above the close 26 bars ago (Chikou crossing the price as of 26 bars ago), short on a cross below; exit on the opposite cross.",
        source_name="Wikipedia — Ichimoku Kinko Hyo (Chikou span)",
        source_url="https://en.wikipedia.org/wiki/Ichimoku_Kink%C5%8D_Hy%C5%8D",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
