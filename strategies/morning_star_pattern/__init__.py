"""Morning/Evening Star: registration + re-exports."""

from strategies.morning_star_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Morning/Evening Star",
        slug="morning_star_pattern",
        description="Steve Nison's Morning/Evening Star 3-candle reversal: long red body (>= 0.6x ATR(14)), small middle body (<= 0.3x candle1), long green close beyond candle1's body midpoint, with close below SMA(50); evening star is the mirror with close above SMA(50). No gap requirement (24/7 crypto). Exit on the opposite star or via the ATR stop/trail.",
        source_name="TradeLabsAI — Morning Star and Evening Star candlesticks",
        source_url="https://learn.tradelabsai.com/candlesticks/morning-star-and-evening-star/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
