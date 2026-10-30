"""VWAP std bands: registration + re-exports."""

from strategies.vwap_std_bands import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="VWAP Std Bands",
        slug="vwap_std_bands",
        description=(
            "UTC-day session VWAP with +/-1 sigma and +/-2 sigma "
            "bands, sigma being the 20-bar rolling standard "
            "deviation of (close - VWAP) as the practical proxy "
            "for the std of (typical price - VWAP). Long when a "
            "close that breached the -2 sigma band closes back "
            "above it; short on the mirror at +2 sigma. Exit "
            "at the VWAP midline. 2xATR stop, 2.5xATR trail, "
            "120-bar max hold."
        ),
        source_name="VWAP (StockCharts ChartSchool, technical indicators: VWAP)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:vwap",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
