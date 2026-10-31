"""Hull Moving Average cross: registration + re-exports."""

from strategies.hull_ma_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hull MA Cross",
        slug="hull_ma_cross",
        description=(
            "Alan Hull's low-lag moving average cross: HMA(16) above "
            "HMA(64) is an uptrend, below is a downtrend. Long on the "
            "bullish HMA cross, short on the bearish cross, exit on "
            "the opposite cross. 2xATR stop, 2.5xATR trail, 120-bar "
            "max hold."
        ),
        source_name="Hull Moving Average (Alan Hull, 2005)",
        source_url="https://capital.com/en-int/learn/technical-analysis/hull-moving-average",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
