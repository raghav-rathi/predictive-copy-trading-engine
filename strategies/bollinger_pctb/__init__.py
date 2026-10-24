"""Bollinger %B band-tag reclaim: registration + re-exports."""

from strategies.bollinger_pctb import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger %B Band-Tag Reclaim",
        slug="bollinger_pctb",
        description=(
            "Bollinger %B (20, 2.0) band-tag reclaim on 1h crypto bars. "
            "LONG when %B crosses back above 0 from below (lower-band "
            "tag reclaimed); SHORT when %B crosses back below 1 from "
            "above. Exit on the mid-band (0.5) cross. 1.5xATR stop, "
            "2xATR chandelier trail, 72-bar (~3-day) max hold."
        ),
        source_name="StockCharts Bollinger Bands / %B",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
