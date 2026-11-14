"""Kase DevStop engine: registration + re-exports."""

from strategies.kase_devstop import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kase DevStop",
        slug="kase_devstop",
        description=(
            "Kase DevStop (Cynthia Kase, Trading with the Odds, 1996): "
            "DTR = two-bar true range, band = mean(DTR,30) + 1.0*stddev "
            "(sample); long stop = ratcheted highest-high-since-flip "
            "minus band, short stop = ratcheted lowest-low-since-flip "
            "plus band; flip long on a close above the short stop, "
            "flip short on a close below the long stop; the DevStop "
            "line IS the exit. Harness stop widened to 6xATR as a "
            "disaster backstop only, no trail, 300-bar max hold."
        ),
        source_name="Kase DevStop (Cynthia Kase, Trading with the Odds, 1996)",
        source_url="https://docs.wickra.org/Indicators/Indicator-KaseDevStop",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
