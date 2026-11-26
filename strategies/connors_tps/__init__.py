"""Connors TPS engine: registration + re-exports."""

from strategies.connors_tps import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Connors TPS",
        slug="connors_tps",
        description=(
            "Connors & Alvarez TPS (Trend, Pullback, Setup): "
            "close above SMA(200) with RSI(2) below 25 for two "
            "consecutive bars goes long (mirror for shorts); exit "
            "when RSI(2) closes above 70 / below 30 or after a "
            "10-bar time exit; 2xATR stop, 3xATR trail."
        ),
        source_name="Larry Connors & Cesar Alvarez — Short Term Trading Strategies That Work (2008)",
        source_url="https://tradingstrategyguides.com/tps-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
