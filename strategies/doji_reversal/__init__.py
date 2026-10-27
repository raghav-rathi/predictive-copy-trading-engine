"""Doji Reversal: registration + re-exports."""

from strategies.doji_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Doji Reversal",
        slug="doji_reversal",
        description=(
            "Nison doji reversal: a doji (body <= 10% of range) printing at a fresh 10-bar extreme after a 3-bar trend — long at a low extreme after a decline, short at a high extreme after a rise; exit on the opposite doji."
        ),
        source_name="Steve Nison doji (Japanese Candlestick Charting Techniques)",
        source_url="https://www.investopedia.com/terms/d/doji.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
