"""Keltner Channel Breakout: registration + re-exports."""

from strategies.keltner_channel_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner Channel Breakout",
        slug="keltner_channel_breakout",
        description="Chester Keltner channel breakout (1960), ATR form popularized by Linda Raschke: long when the close breaks above EMA(20) + 2.0*ATR(10), short below EMA(20) - 2.0*ATR(10); exit on the close back inside the channel, with the harness stop/trail as the exit mechanism.",
        source_name="Chester Keltner — Keltner Channel, How to Make Money in Commodities (1960)",
        source_url="https://www.investopedia.com/terms/k/keltnerchannel.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
