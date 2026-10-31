"""Choppiness Index: registration + re-exports."""

from strategies.choppiness_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Choppiness Index",
        slug="choppiness_index",
        description=(
            "Dreiss Choppiness Index regime filter + Donchian breakout: "
            "enter a breakout only while CHOP(14) < 38.2 (trending regime), "
            "long on a close above the prior Donchian(20) high, short on a "
            "close below the prior Donchian(20) low; exit when CHOP crosses "
            "above 61.8 or price crosses the opposite prior Donchian band. "
            "2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Choppiness Index (LuxAlgo library)",
        source_url="https://www.LuxAlgo.com/library/concept/choppiness-index/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
