"""Voss Predictive Filter: Ehlers' negative-group-delay cycle predictor (registration + re-exports)."""

from strategies.voss_predictive_filter import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Voss Predictive Filter",
        slug="voss_predictive_filter",
        description="John Ehlers' Voss Predictive Filter (TASC Aug 2019): a 2-pole band-pass filter (period 20, bandwidth 0.25) fed into the Voss predictor (predict 3, order 9). Long on Voss crossing above the band-pass line, short on a cross below, entries gated by ADX(14) < 25; exit on the opposite cross.",
        source_name="John F. Ehlers — A Peek Into The Future (TASC Aug 2019)",
        source_url="https://www.fmz.com/strategy/427275",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
