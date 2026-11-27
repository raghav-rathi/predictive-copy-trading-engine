"""NR7 volatility-expansion engine: registration + re-exports."""

from strategies.atr_expansion_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ATR Expansion Breakout (NR7)",
        slug="atr_expansion_breakout",
        description=(
            "Toby Crabel NR7: the narrowest-range bar of the "
            "last 7 arms a high/low bracket; a close crossing "
            "above the NR7 high (long) or below the NR7 low "
            "(short) within the next 3 bars enters the "
            "volatility expansion. Exit on a close back "
            "through the arming NR7 level or the opposite "
            "entry; 2xATR stop, 3xATR trail, 48-bar max hold."
        ),
        source_name="NR4/NR7 strategy — Trading Strategy Guides / LoomiAI",
        source_url="https://tradingstrategyguides.com/narrow-range-bars-the-nr4-and-nr7-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
