"""Prior UTC-day high/low breakout engine: registration + re-exports."""

from strategies.prev_day_high_low import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Prior Day High/Low Breakout",
        slug="prev_day_high_low",
        description=(
            "Prior UTC-day high/low breakout: long a 1h close above "
            "the prior UTC-day high + 0.1% filter, short a close below "
            "the prior UTC-day low - 0.1%; skip days whose range is "
            "< 0.5x its 20-day median; exit on a close back inside the "
            "range, the opposite level breaking, or UTC midnight flat; "
            "1.5xATR stop (approx. just inside the broken level), "
            "3xATR target (2R), 24-bar max hold."
        ),
        source_name="PDH/PDL Breakout",
        source_url="https://www.quantsapp.com/backtesting/strategies/pdh-pdl-breakout-futures-and-option-buy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
