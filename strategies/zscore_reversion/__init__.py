"""Z-Score Reversion: registration + re-exports."""

from strategies.zscore_reversion import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Z-Score Reversion",
        slug="zscore_reversion",
        description=(
            "Bollinger z-score mean reversion: z = (close - SMA(20)) / std(20). Long when z crosses below -2, short when z crosses above +2, exit when z reverts to zero. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Bollinger z-score mean reversion",
        source_url="https://financefeeds.com/crypto-mean-reversion-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
