"""Harmonic Gartley engine: registration + re-exports."""

from strategies.harmonic_gartley import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Harmonic Gartley XABCD",
        slug="harmonic_gartley",
        description=(
            "5-bar-confirmed zigzag pivots scanned as XABCD: AB=0.618*XA, "
            "BC in [0.382,0.886]*AB, CD in [1.272,1.618]*BC, AD=0.786*XA "
            "(+-6% tolerance); long on bullish PRZ completion, short on "
            "bearish; exit on opposite pattern; 2xATR stop (proxy for "
            "stop-beyond-X), 4xATR target, 100-bar max hold."
        ),
        source_name="Gartley pattern guide (ebc.com)",
        source_url="https://www.ebc.com/forex/gartley-pattern-explained-a-guide-to-this-powerful-setup",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
