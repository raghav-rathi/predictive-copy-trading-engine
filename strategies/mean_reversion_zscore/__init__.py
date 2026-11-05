"""Z-score mean reversion: registration + re-exports."""

from strategies.mean_reversion_zscore import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Mean Reversion Z-Score",
        slug="mean_reversion_zscore",
        description="Z-score mean reversion: z = (close - SMA(20)) / std(20). Long when z crosses back above -2 after being below -2 (stretched oversold, reverting); short when z crosses back below +2 after being above +2. Exit when z crosses 0 (back to the mean). Regime guard: longs only when the SMA(50) slope is flat-to-up and shorts only when it is flat-to-down, keeping the fade out of strong trends.",
        source_name="Mean reversion trading (Velotrade)",
        source_url="https://velotrade.com/blog/mean-reversion-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
