"""Kicker pattern: registration + re-exports."""

from strategies.kicker_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kicker Pattern",
        slug="kicker_pattern",
        description=(
            "Steve Nison kicker (kicking) reversal: a candle running "
            "with the trend followed by a strong opposite-direction "
            "candle that gaps beyond the first candle's open "
            "(bullish: black then white with o2 > o1; bearish "
            "mirror), second body at least half its range. Exit on "
            "the opposite kicker. 2xATR stop, 2.5xATR trail, 72-bar "
            "max hold."
        ),
        source_name="Kicker / kicking pattern (Steve Nison, Japanese Candlestick Charting Techniques; CentralCharts candlestick reference)",
        source_url="https://www.centralcharts.com/en/gm/1-learn/7-technical-analysis/28-japanese-candlesticks/552-kicking",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
