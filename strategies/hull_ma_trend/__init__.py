"""Hull Moving Average trend: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.hull_ma_trend import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hull Moving Average Trend",
        slug="hull_ma_trend",
        description=(
            "Hull MA trend (Alan Hull, 2005): LONG when close is above "
            "HMA(16) with HMA(16) rising and close above HMA(64); SHORT "
            "on the mirror. Exits on a close back through HMA(16) or "
            "HMA(16) turning against the position. Transition-only "
            "entries via a position state machine. The HMA halves lag "
            "versus an EMA of the same length, which is the whole point "
            "of the indicator."
        ),
        source_name="Alan Hull, Hull Moving Average (2005)",
        source_url="https://alanhull.com/hull-moving-average",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
