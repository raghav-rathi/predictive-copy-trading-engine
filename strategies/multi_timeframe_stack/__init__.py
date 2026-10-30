"""Multi-timeframe stack: registration + re-exports."""

from strategies.multi_timeframe_stack import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Multi-Timeframe Stack",
        slug="multi_timeframe_stack",
        description=(
            "4h trend filter + 1h entry: 4h EMA(20) above EMA(50) is an "
            "uptrend, below is a downtrend (4h bars formed causally "
            "from groups of 4 1h bars). Long on a 1h EMA(9)/EMA(21) "
            "bullish cross in a 4h uptrend, short on the mirror, exit "
            "on the opposite 1h cross. 2xATR stop, 2.5xATR trail, "
            "120-bar max hold."
        ),
        source_name="Multiple timeframe analysis (Collin Seow guide)",
        source_url="https://collinseow.com/multi-timeframe-analysis/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
