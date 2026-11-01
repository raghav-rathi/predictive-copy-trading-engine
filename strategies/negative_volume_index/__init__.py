"""Negative Volume Index: registration + re-exports."""

from strategies.negative_volume_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Negative Volume Index",
        slug="negative_volume_index",
        description=(
            "Paul Dysart's Negative Volume Index (Fosback version): the cumulative price change on decreasing-volume bars only, starting at 1000, against its 255-bar EMA. Long when NVI crosses above its EMA, short below. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Negative Volume Index (Paul Dysart / Norman Fosback)",
        source_url="https://www.daytrading.com/nvi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
