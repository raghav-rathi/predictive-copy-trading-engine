"""Follow-Through Day engine: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.follow_through_day import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Follow-Through Day (O'Neil)",
        slug="follow_through_day",
        description=(
            "William O'Neil follow-through day, scaled from daily "
            "to 1h bars (1 day = 24 bars): after a >=8% correction "
            "and a new 20-day low, the first up-close day starts "
            "a rally attempt; on attempt-day 4-7 a day gaining "
            ">=1.5% on rising volume confirms the rally (long). "
            "Exit when a later day's close undercuts the "
            "attempt low; 2xATR stop, 3xATR trail, 240-bar max hold."
        ),
        source_name="Follow-Through Day — William O'Neil, How to Make Money in Stocks",
        source_url="https://traderlion.com/trading-strategies/follow-through-day/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
