"""HalfTrend: registration + re-exports."""

from strategies.halftrend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="HalfTrend",
        slug="halftrend",
        description=(
            "Everget HalfTrend trailing-stop trend system: amplitude-2 "
            "price extremes plus SMA(high/low) confirmation drive a "
            "two-state trend machine; long on a down->up trend flip, "
            "short on an up->down flip, exit on the opposite flip. "
            "ATR(100)/2 channels are plotted for context only. 2xATR "
            "stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Everget HalfTrend (TradingView open-source indicator)",
        source_url="https://deepwiki.com/everget/tradingview-pinescript-indicators/2.1.2-halftrend",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
