"""Volume Price Trend: registration + re-exports."""

from strategies.volume_price_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume Price Trend",
        slug="volume_price_trend",
        description=(
            "Volume Price Trend (PVT): the running total of each bar's percentage price change multiplied by its volume. Rising PVT means volume-backed buying. Long when PVT crosses above its 20-bar average, short below. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Price Volume Trend (PVT)",
        source_url="https://docs.prorealalgos.com/pvt.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
