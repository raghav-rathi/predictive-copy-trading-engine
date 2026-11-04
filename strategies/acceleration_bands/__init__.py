"""Acceleration Bands: registration + re-exports."""

from strategies.acceleration_bands import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Acceleration Bands",
        slug="acceleration_bands",
        description="Price Headley Acceleration Bands (20, factor 4): upper = SMA(20) of high*(1+4*(h-l)/(h+l)), lower = SMA(20) of low*(1-4*(h-l)/(h+l)), midline = SMA(20) of close. Two consecutive closes outside a band start an acceleration phase (entry); the first close back inside ends it (exit).",
        source_name="Acceleration Bands (Price Headley)",
        source_url="https://www.luxalgo.com/library/concept/acceleration-bands/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
