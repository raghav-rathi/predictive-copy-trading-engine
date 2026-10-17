"""FRAMA engine: registration + re-exports."""

from strategies.frama import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers FRAMA fractal-adaptive trend system",
        slug="frama",
        description=(
            "Fractal-dimension-adaptive average (N=16): close crossing "
            "FRAMA with slope and 100-bar SMA confirmation; exit on the "
            "cross back."
        ),
        source_name="John Ehlers — Fractal Adaptive Moving Average (FRAMA)",
        source_url="https://www.slideserve.com/mark-barnes/presented-by-john-ehlers-powerpoint-ppt-presentation",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
