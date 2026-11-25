"""Chaikin Money Flow + session VWAP engine: registration + re-exports."""

from strategies.chaikin_vwap_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chaikin VWAP Combo",
        slug="chaikin_vwap_combo",
        description=(
            "Marc Chaikin's Chaikin Money Flow (CMF(20)) confirmed by "
            "the UTC-day session VWAP: long when CMF crosses above "
            "zero with the close above day VWAP, short when CMF "
            "crosses below zero with the close below day VWAP; exit "
            "when CMF crosses back through zero or the close crosses "
            "the day VWAP against the position; 2xATR stop, 3xATR "
            "trail, 60-bar max hold."
        ),
        source_name="Marc Chaikin, Chaikin Money Flow (StockCharts ChartSchool)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:chaikin_money_flow_cmf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
