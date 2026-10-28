"""Pennant continuation pattern: registration + re-exports."""

from strategies.pennant_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pennant Pattern",
        slug="pennant_pattern",
        description=(
            "Classic pennant: a completed 5-bar pole of >=3x ATR(14), "
            "then a 5-15 bar converging range (3-bar blocks: highs "
            "falling, lows rising), then a breakout close beyond the "
            "range high/low with volume > 1.2x the 20-bar average. "
            "Exit on the opposite breakout or 168-bar max hold. "
            "2xATR stop, 2.5xATR trail."
        ),
        source_name="Classic pennant continuation (Edwards & Magee / StockCharts)",
        source_url="https://school.stockcharts.com/doku.php?id=chart_analysis:chart_patterns:pennant_continuation",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
