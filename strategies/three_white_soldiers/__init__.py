"""Three white soldiers: registration + re-exports."""

from strategies.three_white_soldiers import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Three White Soldiers",
        slug="three_white_soldiers",
        description="Three white soldiers after a downtrend (close below SMA(50) for 5 bars): three consecutive bullish candles, each closing higher, opening inside the previous body, with a small upper wick and a body of at least 0.5x ATR(14) — enter long on the 3rd close; exit on a close below the 1st soldier's open. Mirror with three black crows for shorts.",
        source_name="TMGM — Three White Soldiers Pattern",
        source_url="https://www.tmgm.com/en/academy/trading-academy/three-white-soldiers-candlestick-pattern",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
