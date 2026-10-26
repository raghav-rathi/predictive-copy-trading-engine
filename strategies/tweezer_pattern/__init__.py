"""Tweezer Top / Bottom: registration + re-exports."""

from strategies.tweezer_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Tweezer Top / Bottom",
        slug="tweezer_pattern",
        description=(
            "Nison tweezers: two consecutive bars sharing (within 0.15%) a high at a top or a low at a bottom, with the second bar closing back inside."
        ),
        source_name="Steve Nison, Japanese Candlestick Charting Techniques (Tweezers Tops and Bottoms)",
        source_url="https://epage.pub/doc/6-japanese-candlestick-charting-techniques-by-steve-nison-yvm9x4p2dy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
