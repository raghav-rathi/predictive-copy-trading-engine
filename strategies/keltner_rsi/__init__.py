"""Keltner channel + RSI: registration + re-exports."""

from strategies.keltner_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner Channel + RSI",
        slug="keltner_rsi",
        description="Long when close breaks above the Keltner upper band (EMA20, ATR10, 1.5x) with RSI(14) in [50,75]; short mirror with RSI in [25,50]; exit at the Keltner mid-band cross. 2xATR stop, 2.5xATR trail, 168-bar max hold.",
        source_name="Keltner channels (Chester Keltner; Linda Raschke) + RSI (J. Welles Wilder)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/keltner-channels",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
