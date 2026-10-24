"""TTM-style squeeze breakout: registration + re-exports."""

from strategies.keltner_squeeze import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TTM-Style Keltner Squeeze Breakout",
        slug="keltner_squeeze",
        description=(
            "TTM-style squeeze breakout on 1h crypto bars: squeeze ON "
            "when Bollinger Band(20, 2.0) width < Keltner Channel "
            "(EMA20 +/- 1.5xATR10) width. LONG when the squeeze was "
            "on within the last 3 bars and close breaks above the "
            "Bollinger upper band; SHORT on the mirror. Exit on the "
            "opposite band cross. 2.0xATR stop, 2.5xATR chandelier "
            "trail, 96-bar (~4-day) max hold."
        ),
        source_name="TTM Squeeze (John Carter) / StockCharts Keltner Channels",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
