"""Detrended Price Oscillator engine: registration + re-exports."""

from strategies.dpo_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Detrended Price Oscillator cycle system",
        slug="dpo_cycle",
        description=(
            "DPO(21) = close minus the 21-bar SMA from 11 bars ago "
            "(causal displacement); long on the zero cross up, short on the "
            "cross down; exit on the opposite cross."
        ),
        source_name="Detrended Price Oscillator (ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
