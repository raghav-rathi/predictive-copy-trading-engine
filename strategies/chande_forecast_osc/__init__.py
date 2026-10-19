"""Chande Forecast Oscillator engine: registration + re-exports."""

from strategies.chande_forecast_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande Forecast Oscillator",
        slug="chande_forecast_osc",
        description=(
            "n=20 linear-regression time-series forecast of close, "
            "one-step-ahead; FO = (close - forecast)/close*100; 3-bar SMA "
            "signal; long on FO crossing above signal with FO>0, short on "
            "cross below with FO<0; exit on cross back; 2xATR stop, 40-bar "
            "max hold."
        ),
        source_name="MQL5 CodeBase 21827 — Chande Forecast Oscillator",
        source_url="https://www.mql5.com/en/code/21827",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
