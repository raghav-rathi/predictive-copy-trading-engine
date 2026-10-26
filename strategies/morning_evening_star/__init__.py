"""Morning Star / Evening Star: registration + re-exports."""

from strategies.morning_evening_star import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Morning Star / Evening Star",
        slug="morning_evening_star",
        description=(
            "Nison star reversal: a large candle, a small-bodied star that gaps away, and a third candle closing past the first candle's midpoint."
        ),
        source_name="Steve Nison, Japanese Candlestick Charting Techniques (Morning/Evening Star)",
        source_url="https://epage.pub/doc/6-japanese-candlestick-charting-techniques-by-steve-nison-yvm9x4p2dy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
