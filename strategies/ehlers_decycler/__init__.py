"""Decycler trend engine: registration + re-exports."""

from strategies.ehlers_decycler import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Decycler Trend",
        slug="ehlers_decycler",
        description=(
            "Decycler (Ehlers): 2-pole Butterworth high-pass of close "
            "stripped from price to leave the zero-lag trend component; "
            "long when close crosses above the decycler while it is "
            "rising, short when close crosses below while it is falling; "
            "exits on the opposite cross; 2xATR stop, 2xATR chandelier "
            "trail, 150-bar max hold."
        ),
        source_name="Decycler (John Ehlers, TASC Sep 2015)",
        source_url="https://ar.tradingview.com/scripts/ehlers/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
