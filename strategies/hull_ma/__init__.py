"""HMA engine: registration + re-exports."""

from strategies.hull_ma import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hull Moving Average trend system",
        slug="hull_ma",
        description=(
            "HMA(16); long when close crosses above a rising HMA; short "
            "when close crosses below a falling HMA; exit on opposite "
            "cross or HMA slope flip."
        ),
        source_name="Alan Hull — Hull Moving Average",
        source_url="https://alanhull.com/hull-moving-average",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
