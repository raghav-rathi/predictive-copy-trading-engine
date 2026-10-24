"""Golden Cross / Death Cross: registration + re-exports."""

from strategies.golden_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Golden Cross / Death Cross",
        slug="golden_cross",
        description=(
            "Classic SMA(50)/SMA(200) cross on 1h crypto bars. LONG "
            "when SMA50 crosses above SMA200 (Golden Cross); SHORT "
            "when SMA50 crosses below SMA200 (Death Cross). Exit on "
            "the opposite cross. 2.0xATR stop, 3.0xATR chandelier "
            "trail, 240-bar (~10-day) max hold."
        ),
        source_name="Golden Cross / Death Cross (classic SMA cross)",
        source_url="https://www.investopedia.com/terms/g/goldencross.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
