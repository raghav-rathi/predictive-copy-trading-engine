"""Bollinger Band squeeze breakout: registration + re-exports."""

from strategies.bollinger_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger Band Squeeze Breakout",
        slug="bollinger_breakout",
        description="John Bollinger's squeeze breakout: BB(20, 2) with BandWidth (upper-lower)/mid in the lowest 15% of the last 50 bars marking a squeeze; entry only while a squeeze is armed (within 10 bars): close above the upper band goes long, close below the lower band goes short; exit when the close comes back inside the bands.",
        source_name="Bollinger Band squeeze breakout strategy (Traderspy)",
        source_url="https://blog.traderspy.app/en/blog/bollinger-band-squeeze-breakout-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
