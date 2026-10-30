"""Asian-range breakout: registration + re-exports."""

from strategies.asian_range_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Asian Range Breakout",
        slug="asian_range_breakout",
        description=(
            "Asian-session range breakout adapted to 24/7 "
            "crypto: for each UTC day the Asian range is the "
            "high/low of bars with UTC hour in [0, 8). Long "
            "on the first 1h bar after 08:00 UTC whose close "
            "breaks above that day's Asian range high with "
            "volume above its 20-bar average; short mirrored "
            "below the range low. Exit at the 16:00 UTC bar "
            "or the risk layer's trail. 2xATR stop, 2.5xATR "
            "trail, 24-bar max hold."
        ),
        source_name="Asian Session High Low Breakout Strategy (FMZ)",
        source_url="https://www.fmz.com/lang/en/strategy/446567",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
