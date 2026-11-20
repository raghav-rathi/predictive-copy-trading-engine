"""Heikin Ashi + EMA: registration + re-exports."""

from strategies.heikin_ashi_ema import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Heikin Ashi EMA",
        slug="heikin_ashi_ema",
        description="Heikin Ashi candles plus an EMA trend filter: long on a bullish HA candle with EMA(9) > EMA(21) and close > EMA(50); short mirrored. Exit when the HA candle flips direction or the EMA(9)/EMA(21) cross turns against, plus the harness stop/trail.",
        source_name="Heikin Ashi candles + EMA trend filter",
        source_url="https://en.wikipedia.org/wiki/Heikin_Ashi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
