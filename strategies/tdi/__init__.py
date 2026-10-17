"""TDI engine: registration + re-exports."""

from strategies.tdi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dean Malone Traders Dynamic Index system",
        slug="tdi",
        description=(
            "RSI(13) green vs SMA(2) red crosses, gated by the SMA(34) "
            "yellow market-base line at 50; exit on the reverse cross or "
            "at RSI 68/32."
        ),
        source_name="Dean Malone — Traders Dynamic Index (CompassFX E.A.S.Y.)",
        source_url="https://www.forexracer.com/traders-dynamic-index-tdi-indicator-mt4/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
