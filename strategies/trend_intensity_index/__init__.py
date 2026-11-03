"""Trend Intensity Index: registration + re-exports."""

from strategies.trend_intensity_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Trend Intensity Index",
        slug="trend_intensity_index",
        description=(
            "M.H. Pee Trend Intensity Index (30): 100 x sum of up-moves / sum of absolute moves. Long on cross above 80 (strong uptrend), short on cross below 20 (strong downtrend); exits on cross back through 50."
        ),
        source_name="Trend Intensity Index (M.H. Pee)",
        source_url="https://www.incrediblecharts.com/indicators/trend_intensity_index.php",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
