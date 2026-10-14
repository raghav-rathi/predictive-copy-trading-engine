"""Pretty Good Oscillator engine: registration + re-exports."""

from strategies.pgo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pretty Good Oscillator breakout system",
        slug="pgo",
        description=(
            "PGO = (close - SMA(14)) / ATR(14); long when it crosses above "
            "+1.0, short when it crosses below -1.0; exit on the zero-line "
            "cross back."
        ),
        source_name="Mark Johnson — Pretty Good Oscillator",
        source_url="https://library.tradingtechnologies.com/trade/chrt-ti-pretty-good-oscillator.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
