"""Chande Momentum Oscillator engine: registration + re-exports."""

from strategies.chande_cmo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande Momentum Oscillator extreme-cross system",
        slug="chande_cmo",
        description=(
            "CMO(14) = 100*(Su-Sd)/(Su+Sd); long when it crosses above -50, "
            "short when it crosses below +50; exit on the zero-line cross "
            "back."
        ),
        source_name="Tushar Chande — Chande Momentum Oscillator (1994)",
        source_url="https://gocharting.com/docs/charting/technical-indicator/momentum/chande-momentum-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
