"""RSI Trendline Break: registration + re-exports."""

from strategies.rsi_trendline import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI Trendline Break",
        slug="rsi_trendline",
        description=(
            "RSI(14) trendline break: a descending line through the last two confirmed RSI swing highs breaks upward for longs; an ascending line through the last two confirmed RSI swing lows breaks downward for shorts."
        ),
        source_name="RSI trendline analysis (Wilder RSI applied to its own trendlines; Murphy)",
        source_url="https://www.investopedia.com/terms/r/rsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
