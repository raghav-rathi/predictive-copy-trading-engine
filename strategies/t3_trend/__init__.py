"""Tillson T3 engine: registration + re-exports."""

from strategies.t3_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Tillson T3 cross (Tillson)",
        slug="t3_trend",
        description=(
            "Six-chained-EMA T3 smoother (a=0.7); T3(5)/T3(15) cross "
            "entries; exits on the opposite cross; 2xATR stop, 96-bar "
            "max hold."
        ),
        source_name="T3 Moving Average — TradingPedia / TA-Lib docs",
        source_url="https://www.tradingpedia.com/forex-trading-indicators/t3-moving-average-indicator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
