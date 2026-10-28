"""Smoothed Heikin-Ashi: registration + re-exports."""

from strategies.heikin_ashi_smoothed import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Smoothed Heikin-Ashi",
        slug="heikin_ashi_smoothed",
        description=(
            "Heikin-Ashi candles with ha_open and ha_close each "
            "smoothed by EMA(5). Long when smoothed HA close crosses "
            "above smoothed HA open, short on the cross below; exit "
            "on the opposite cross. 2xATR stop, 2.5xATR trail, "
            "168-bar max hold."
        ),
        source_name="Heikin-Ashi + EMA smoothing (standard smoothed-HA variant)",
        source_url="https://en.wikipedia.org/wiki/Heikin_Ashi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
