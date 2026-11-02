"""Hull Suite: registration + re-exports."""

from strategies.hull_suite import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hull Suite",
        slug="hull_suite",
        description=(
            "InSilico Hull Suite: HMA(16) slope turn (rising vs falling) as the signal, with ATR bands for context; long on the turn up, short on the turn down."
        ),
        source_name="Hull Suite (InSilico) / Hull Moving Average (Alan Hull)",
        source_url="https://arrowalgo.com/hull-moving-average-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
