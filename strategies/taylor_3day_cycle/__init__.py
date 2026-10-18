"""Taylor 3-day cycle engine: registration + re-exports."""

from strategies.taylor_3day_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Taylor 3-Day Book Method",
        slug="taylor_3day_cycle",
        description=(
            "George Douglass Taylor's 3-day rhythm on NY time: Buy-Day "
            "longs on dips to the prior day's low, Sell Day quiet, "
            "Sell-Short-Day shorts on rallies to the prior day's high, "
            "with -1-day re-phasing when a Buy Day misses; 1xATR stop, "
            "24-bar max hold."
        ),
        source_name="George Douglass Taylor, The Taylor Trading Technique (1950)",
        source_url="https://www.smbtraining.com/blog/the-taylor-rhythm",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
