"""Ehlers Relative Vigor Index engine: registration + re-exports."""

from strategies.rvi_ehlers import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers Relative Vigor Index cross",
        slug="rvi_ehlers",
        description=(
            "Ehlers RVI = SMA10 of (c-o)/(h-l) with a 1-2-2-1 weighted "
            "signal line; entries on RVI/signal crosses; optional minimum "
            "separation filter vs whipsaw; 2xATR stop, 72-bar max hold."
        ),
        source_name="Relative Vigor Index — John Ehlers, S&C Jan 2002",
        source_url="https://www.tradingpedia.com/forex-trading-indicators/ehlers-relative-vigor-index/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
