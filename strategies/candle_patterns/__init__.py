"""Candlestick-pattern engine: registration + re-exports."""

from strategies.candle_patterns import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Nison candlestick pattern reversal system",
        slug="candle_patterns",
        description=(
            "Bullish/bearish engulfing (body engulfs prior body) and pin "
            "bars (wick >= 2x body, body in the favorable third, range >= "
            "0.5x ATR); enter the pattern, exit on the opposite pattern."
        ),
        source_name="Steve Nison — Japanese candlestick patterns (engulfing, pin bar)",
        source_url="https://www.investopedia.com/terms/b/bullish-engulfing-pattern.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
