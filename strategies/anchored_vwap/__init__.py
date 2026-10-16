"""Anchored VWAP reclaim engine: registration + re-exports."""

from strategies.anchored_vwap import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Anchored VWAP reclaim (Shannon)",
        slug="anchored_vwap",
        description=(
            "VWAP anchored to the most recent confirmed 51-bar fractal "
            "swing extreme (bull/bear anchors, active = newest); entries "
            "on genuine reclaims of the anchor VWAP with a rising 5-bar "
            "slope; 2xATR stop, 3xATR trail, 72-bar max hold."
        ),
        source_name="Technical Analysis Using Multiple Timeframes — Brian Shannon (2008)",
        source_url="https://www.tradingview.com/script/oSfy3h8d-Brian-Shannon-Market-Structure-Reversal-Engine/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
