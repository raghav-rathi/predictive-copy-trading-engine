"""Hammer / Shooting Star: registration + re-exports."""

from strategies.hammer_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hammer / Shooting Star",
        slug="hammer_pattern",
        description=(
            "Nison hammer (long) / shooting star (short): a small body in the upper (lower) third of the range with a lower (upper) shadow at least twice the body, after a 3-bar trend; entry on the pattern close, exit on the opposite pattern."
        ),
        source_name="Steve Nison hammer & shooting star (Japanese Candlestick Charting Techniques)",
        source_url="https://www.investopedia.com/terms/h/hammer.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
