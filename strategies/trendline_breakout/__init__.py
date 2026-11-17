"""Demark-style trendline breakout: registration + re-exports."""

from strategies.trendline_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Trendline Breakout",
        slug="trendline_breakout",
        description="Demark-style trendline breaks: 10-bar swing pivots (5 bars each side, confirmed 5 bars after forming); downtrend line through the last two swing highs, uptrend line through the last two swing lows. Long on a close crossing above the downtrend line, short on a close crossing below the uptrend line; exit on the opposite line break, plus the harness stop/trail.",
        source_name="Demark TD trendlines / trendline breaks",
        source_url="https://www.investopedia.com/terms/t/trendline.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
