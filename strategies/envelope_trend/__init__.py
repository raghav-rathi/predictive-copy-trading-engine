"""Moving-average envelope breakout: registration + re-exports."""

from strategies.envelope_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MA Envelope Breakout",
        slug="envelope_trend",
        description=(
            "Percentage envelope breakout: long on a close above SMA(20) x "
            "1.05, short on a close below SMA(20) x 0.95, exit on a close "
            "back through the midline. 2xATR stop, 2.5xATR trail, 120-bar "
            "max hold."
        ),
        source_name="Moving-average envelopes (Murphy, Technical Analysis of the Financial Markets)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
