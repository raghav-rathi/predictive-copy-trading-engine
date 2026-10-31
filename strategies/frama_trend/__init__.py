"""FRAMA trend: registration + re-exports."""

from strategies.frama_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="FRAMA Trend",
        slug="frama_trend",
        description=(
            "John Ehlers Fractal Adaptive Moving Average, N=16: the "
            "smoothing factor adapts to the fractal dimension of the "
            "last 16 bars (fast in trends, slow in congestion). Long "
            "on a close cross above FRAMA, short on a cross below, "
            "exit on the opposite cross. 2xATR stop, 2.5xATR trail, "
            "120-bar max hold."
        ),
        source_name="John Ehlers FRAMA (R-bloggers / QuantStrat TradeR writeup)",
        source_url="https://www.r-bloggers.com/2014/06/the-continuing-search-for-robust-momentum-indicators-the-fractal-adaptive-moving-average/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
