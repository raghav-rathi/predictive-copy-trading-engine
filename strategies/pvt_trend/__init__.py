"""Price-Volume Trend engine: registration + re-exports."""

from strategies.pvt_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Price-Volume Trend cross (Granville)",
        slug="pvt_trend",
        description=(
            "PVT = cum(volume * pct_change); entries on PVT crossing its "
            "20-bar SMA; exits on the opposite cross; 2xATR stop, 96-bar "
            "max hold."
        ),
        source_name="Price and Volume Trend (PVT) — MetaQuotes / MultiCharts docs",
        source_url="https://www.mql5.com/en/code/45",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
