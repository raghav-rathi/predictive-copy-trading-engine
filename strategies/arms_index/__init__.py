"""ARMS Index / TRIN engine: registration + re-exports."""

from strategies.arms_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ARMS Index (TRIN)",
        slug="arms_index",
        description=(
            "TRIN on a single-asset candle/volume proxy: (up-bars / "
            "down-bars) / (up-volume / down-volume) over 10 bars. Long "
            "when TRIN crosses below 0.7 after being above 1.0 (panic "
            "washout); short when it crosses above 1.5 after being "
            "below 1.0. Exit on reversion into the 0.9-1.1 band; "
            "1.5xATR stop, 2xATR target, 24-bar max hold."
        ),
        source_name="ARMS Index / TRIN (Richard Arms)",
        source_url="https://investing.university/articles/arms-index-trin/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
