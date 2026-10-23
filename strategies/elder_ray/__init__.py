"""Elder Ray: Bull/Bear Power around EMA(13) -- Dr. Alexander Elder's
momentum gauge from "Trading for a Living" (Triple Screen lineage)."""

from strategies.elder_ray import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Ray Bull/Bear Power",
        slug="elder_ray",
        description=(
            'Dr. Alexander Elder\'s Elder Ray (Trading for a Living, Triple Screen lineage): Bull Power = high - EMA(13), Bear Power = low - EMA(13). Long when EMA(13) is rising and bear power is below zero but rising (buy the dip as the bears lose grip); short mirror when EMA(13) is falling and bull power is above zero but falling. Exit when power crosses zero or the EMA(13) slope reverses. 1.5xATR stop, 2xATR chandelier trail, 120-bar max hold.'
        ),
        source_name="Elder Ray Index (Dr. Alexander Elder)",
        source_url="https://www.incrediblecharts.com/indicators/elder_ray_index.php",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
