"""Tasuki gap pattern: registration + re-exports."""

from strategies.tasuki_gap_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Tasuki Gap Pattern",
        slug="tasuki_gap_pattern",
        description=(
            "Steve Nison tasuki gap continuation: two same-color "
            "candles with a gap in the trend direction, followed by "
            "a counter-color candle that opens inside the second "
            "candle's body and closes between the first candle's "
            "close and the second candle's close, so the gap is "
            "not closed (upside: white, white gap-up, black "
            "retracing; downside mirror), with a 5-bar trend "
            "filter. Exit on the opposite tasuki. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Tasuki gap pattern (Steve Nison, Japanese Candlestick Charting Techniques; Investopedia upside tasuki gap)",
        source_url="https://www.investopedia.com/terms/u/upside-tasuki-gap.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
