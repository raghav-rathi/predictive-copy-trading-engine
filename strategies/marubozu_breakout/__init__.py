"""Marubozu Breakout: registration + re-exports."""

from strategies.marubozu_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Marubozu Breakout",
        slug="marubozu_breakout",
        description=(
            "Nison marubozu: a candle whose body is >= 90% of its range is a conviction candle — long on a bullish marubozu close, short on a bearish one; exit on the opposite marubozu."
        ),
        source_name="Steve Nison marubozu (Japanese Candlestick Charting Techniques)",
        source_url="https://www.investopedia.com/terms/m/marubozu.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
