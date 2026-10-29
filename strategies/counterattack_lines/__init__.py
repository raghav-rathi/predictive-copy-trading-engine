"""Counterattack lines: registration + re-exports."""

from strategies.counterattack_lines import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Counterattack Lines",
        slug="counterattack_lines",
        description=(
            "Steve Nison counterattack lines reversal: after a "
            "5-bar trend, a long candle is followed by an "
            "opposite-color candle of similar size (body ratio "
            "within 2/3–3/2) that gaps against the trend at the "
            "open and closes within 0.2xATR of the prior candle's "
            "close (bullish: black then white; bearish mirror). "
            "Exit on the opposite counterattack. 2xATR stop, "
            "2.5xATR trail, 72-bar max hold."
        ),
        source_name="Counterattack lines (Steve Nison, Japanese Candlestick Charting Techniques, ch. 6)",
        source_url="https://archive.org/stream/JapaneseCandlestickChartingTechniques2ndEditionSteveNison/Japanese%20Candlestick%20Charting%20Techniques%2C%202nd%20Edition%2C%20Steve%20Nison_djvu.txt",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
