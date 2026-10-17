"""VIDYA engine: registration + re-exports."""

from strategies.vidya import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande VIDYA adaptive trend system",
        slug="vidya",
        description=(
            "CMO(9)-weighted adaptive average of close; long on a cross "
            "above VIDYA with rising VIDYA above its 50-bar SMA, mirror for "
            "shorts; exit on the cross back."
        ),
        source_name="Tushar Chande — Variable Index Dynamic Average (VIDYA)",
        source_url="https://www.mql5.com/en/articles/11341?print=",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
