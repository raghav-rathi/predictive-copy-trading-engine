"""Cumulative Volume Delta trend engine: registration + re-exports."""

from strategies.cvd_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="CVD Trend",
        slug="cvd_trend",
        description=(
            "Cumulative Volume Delta trend: close-location proxy "
            "buy_vol=v*(c-l)/(h-l), delta=buy_vol-sell_vol, CVD=cumsum(delta); "
            "long when EMA(CVD,20) slope turns positive (rising 2 bars) "
            "with close above EMA(50), short on the mirror image; exit "
            "when the CVD slope reverses; 2xATR stop, 3xATR chandelier "
            "trail, 150-bar max hold."
        ),
        source_name="Cumulative Volume Delta (CVD)",
        source_url="https://www.quantvps.com/blog/cumulative-volume-delta",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
