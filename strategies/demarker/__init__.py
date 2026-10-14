"""DeMarker exhaustion engine: registration + re-exports."""

from strategies.demarker import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DeMarker exhaustion (DeMark)",
        slug="demarker",
        description=(
            "DeM = SMA(DeMax,14)/(SMA(DeMax,14)+SMA(DeMin,14)); buy the "
            "cross below 0.3, exit above 0.5; mirror shorts. 2xATR stop, "
            "24-bar max hold."
        ),
        source_name="DeMarker (Tom DeMark) — TradingKey definition",
        source_url="https://www.tradingkey.com/dictionary/demarker-indicator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
