"""Heikin Ashi ADX engine: registration + re-exports."""

from strategies.heikin_ashi_adx import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Heikin Ashi ADX",
        slug="heikin_ashi_adx",
        description=(
            "Heikin Ashi candle colour + Wilder ADX(14) trend filter: long on a bullish HA bar with ADX > 25 and +DI > -DI, short on a bearish HA bar with ADX > 25 and -DI > +DI; exit when the HA bar flips against the position or ADX falls below 20; 2xATR stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="Heikin-Ashi chart (Wikipedia) + Wilder ADX",
        source_url="https://en.wikipedia.org/wiki/Heikin-Ashi_chart",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
