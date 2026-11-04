"""Keltner + MACD: registration + re-exports."""

from strategies.keltner_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner + MACD",
        slug="keltner_macd",
        description="Keltner channel (EMA20 +/- 1.5x ATR10) breakout confirmed by MACD: long on a close above the upper Keltner band while MACD is above its signal line; short on a close below the lower band while MACD is below its signal line; exit on a close back through the Keltner midline.",
        source_name="Keltner channel + MACD confirmation",
        source_url="https://www.supermoney.com/encyclopedia/keltner-channel",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
