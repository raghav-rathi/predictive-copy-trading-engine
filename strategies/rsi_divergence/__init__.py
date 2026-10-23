"""RSI(14) swing-pivot divergence: registration + re-exports."""

from strategies.rsi_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI(14) Swing-Pivot Divergence",
        slug="rsi_divergence",
        description=(
            "Classic RSI(14) divergence on confirmed 3/3 swing pivots "
            "(no lookahead: a pivot is usable 3 bars after its center). "
            "Regular bullish (price lower low + RSI higher low) and "
            "hidden bullish (price higher low + RSI lower low) enter "
            "long; regular bearish and hidden bearish enter short, "
            "each firing once on the confirmation bar of the newly "
            "confirmed pivot pair. Longs exit on bearish-divergence "
            "confirmation, shorts on bullish-divergence confirmation; "
            "1.5xATR stop, 2xATR chandelier trail, 96-bar max hold, "
            "both directions enabled."
        ),
        source_name="RSI divergence (TradingSim / TradingView community)",
        source_url="https://www.tradingsim.com/blog/divergence",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
