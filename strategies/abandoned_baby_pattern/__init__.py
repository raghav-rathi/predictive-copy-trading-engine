"""Abandoned baby pattern: registration + re-exports."""

from strategies.abandoned_baby_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Abandoned Baby Pattern",
        slug="abandoned_baby_pattern",
        description=(
            "Nison abandoned baby: gap, doji, gap reversal with "
            "strict non-overlapping gaps, long-body first/third "
            "candles, close past the first candle's midpoint, and "
            "third-bar volume at/above its 20-bar average. Bullish "
            "and bearish variants; exit on the opposite baby. "
            "1.5xATR stop, 2xATR trail, 2.5xATR target, 120-bar "
            "max hold."
        ),
        source_name="Abandoned baby pattern (Steve Nison, Japanese Candlestick Charting Techniques; Investopedia)",
        source_url="https://www.investopedia.com/terms/a/abandonedbaby.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
