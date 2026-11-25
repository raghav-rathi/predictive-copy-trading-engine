"""EMA ribbon expansion engine: registration + re-exports."""

from strategies.ema_ribbon_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EMA Ribbon Expansion",
        slug="ema_ribbon_cross",
        description=(
            "Guppy-style EMA ribbon (8/13/21/34/55): long when the "
            "ribbon is fully aligned bullish and ribbon width was at "
            "its 20-bar minimum within the last 3 bars, short on the "
            "mirror; exit when EMA8 crosses back through EMA13; "
            "2xATR stop, 3xATR trail, 60-bar max hold."
        ),
        source_name="Guppy Multiple Moving Average (Daryl Guppy), ribbon-expansion variant",
        source_url="https://capital.com/en-int/learn/technical-analysis/gmma-indicator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
