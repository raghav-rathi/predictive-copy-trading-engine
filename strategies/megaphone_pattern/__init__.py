"""Megaphone Pattern: registration + re-exports."""

from strategies.megaphone_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Megaphone Pattern",
        slug="megaphone_pattern",
        description="Broadening formation / megaphone (Edwards & Magee): 3 successive higher highs and 3 successive lower lows, alternating, each swing expanding by >= 0.5x ATR; long on a close above the most recent swing high after the 3rd lower low, short on a close below the most recent swing low after the 3rd higher high; exit on a close through the pattern midline.",
        source_name="Broadening Formation / Megaphone (Edwards & Magee, Technical Analysis of Stock Trends)",
        source_url="https://www.luxalgo.com/library/concept/broadening-formation/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
