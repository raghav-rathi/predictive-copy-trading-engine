"""Hurst FLD engine: registration + re-exports."""

from strategies.hurst_fld import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hurst Future Lines of Demarcation",
        slug="hurst_fld",
        description=(
            "FLD(N) = median shifted back N/2 bars; entries on the "
            "price/FLD20/FLD40/FLD80 bullish or bearish cascade, exits "
            "on the cross back through FLD20; 2xATR stop, 72-bar max hold."
        ),
        source_name="J.M. Hurst, The Profit Magic of Stock Transaction Timing",
        source_url="https://notes.hurstcycles.com/from-analysis-to-trading/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
