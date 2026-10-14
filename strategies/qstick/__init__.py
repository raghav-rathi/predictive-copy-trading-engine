"""Qstick engine: registration + re-exports."""

from strategies.qstick import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande Qstick zero-cross system",
        slug="qstick",
        description=(
            "Qstick = 8-bar SMA of (close - open); long when it crosses "
            "above zero, short on the mirror cross below zero; exit on the "
            "opposite cross."
        ),
        source_name="Tushar Chande — Qstick",
        source_url="https://library.tradingtechnologies.com/trade/chrt-ti-qstick.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
