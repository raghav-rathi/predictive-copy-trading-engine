"""ABCD harmonic pattern: registration + re-exports."""

from strategies.abcd_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ABCD Harmonic Pattern",
        slug="abcd_pattern",
        description=(
            "ABCD harmonic pattern on 5-bar zigzag pivots: AB then BC "
            "retracing 38.2%-88.6% of AB, then CD extending 127.2%-"
            "161.8% of BC with |CD| within 20% of |AB|. Bullish "
            "completion (A high, B low, C lower high, D low) -> long; "
            "bearish mirror -> short. Exit on opposite completion or "
            "a 50%-of-CD move past D against the position. 2xATR "
            "stop, 2.5xATR trail, 96-bar max hold."
        ),
        source_name="Harmonic Trading (Scott Carney) — ABCD pattern",
        source_url="https://harmonictrading.com/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
