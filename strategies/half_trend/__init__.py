"""HalfTrend engine: registration + re-exports."""

from strategies.half_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="HalfTrend ATR-channel trend system",
        slug="half_trend",
        description=(
            "Amplitude-based high/low extremes with an ATR(100)/2 x2 "
            "channel; the stateful trend line trails below price in "
            "uptrends and above in downtrends; flips are entries."
        ),
        source_name="everget — HalfTrend (TradingView Pine, open source)",
        source_url="https://deepwiki.com/everget/tradingview-pinescript-indicators/2.1.2-halftrend",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
