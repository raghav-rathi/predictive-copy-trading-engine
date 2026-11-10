"""Andreas Clenow trend following: registration + re-exports."""

from strategies.clenow_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Clenow Trend Following",
        slug="clenow_trend",
        description="Andreas Clenow trend following (Following the Trend): 50/100-day EMA trend filter, enter on a 50-day extreme in the trend direction, exit on a 3x ATR trailing stop or the opposite breakout.",
        source_name="Andreas Clenow — Following the Trend",
        source_url="https://easylanguagemastery.com/strategies/free-trend-following-system-with-indicator-tracker/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
