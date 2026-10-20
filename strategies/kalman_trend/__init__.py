"""Kalman filter trend engine: registration + re-exports."""

from strategies.kalman_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kalman Filter Trend",
        slug="kalman_trend",
        description=(
            "1-D Kalman filter with a price+velocity state on closes; long "
            "when the close crosses above the filter estimate with the "
            "filter already rising, short on the mirror image; exits on the "
            "opposite cross; 2xATR stop, 200-bar max hold."
        ),
        source_name="Kalman Filter trend strategy (DCAUT, TradingView)",
        source_url="https://br.tradingview.com/script/u5C3sDUc-Kalman-Filter-DCAUT/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
