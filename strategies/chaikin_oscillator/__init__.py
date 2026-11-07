"""Chaikin Oscillator: registration + re-exports."""

from strategies.chaikin_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chaikin Oscillator",
        slug="chaikin_oscillator",
        description="Marc Chaikin's Chaikin Oscillator: ADL is the cumulative Money Flow Volume ((c-l)-(h-c))/(h-l)*v, CHO = EMA(3, ADL) - EMA(10, ADL). Long on a CHO cross above zero with close above SMA(50); short on a cross below zero with close below SMA(50). Exit on the reverse zero cross.",
        source_name="MarketInOut — Chaikin Oscillator",
        source_url="https://www.marketinout.com/technical-analysis/chaikin-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
