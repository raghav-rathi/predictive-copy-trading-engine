"""Harami Pattern: registration + re-exports."""

from strategies.harami_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Harami Pattern",
        slug="harami_pattern",
        description=(
            "Nison harami: a large candle followed by a small body fully inside the first body — bullish when the small body is white after black, bearish when black after white."
        ),
        source_name="Steve Nison, Japanese Candlestick Charting Techniques (Harami Pattern)",
        source_url="https://epage.pub/doc/6-japanese-candlestick-charting-techniques-by-steve-nison-yvm9x4p2dy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
