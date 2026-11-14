"""Renko 2-brick reversal engine: registration + re-exports."""

from strategies.renko_brick_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Renko Brick Reversal",
        slug="renko_brick_reversal",
        description=(
            "Renko (classic, close-based approximation): brick size = "
            "mean ATR(14) over the first 200 bars, fixed per coin; "
            "bricks print when the 1h close clears the last brick edge "
            "by one brick size; long on a bullish 2-brick reversal "
            "after >= 3 down bricks, short on a bearish 2-brick "
            "reversal after >= 3 up bricks; exit on the opposite "
            "2-brick reversal; 2xATR stop, 3xATR chandelier trail, "
            "200-bar max hold."
        ),
        source_name="Renko chart",
        source_url="https://www.cmcmarkets.com/en-gb/technical-analysis/renko-charts",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
