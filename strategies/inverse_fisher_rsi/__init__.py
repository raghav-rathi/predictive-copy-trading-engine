"""Inverse Fisher RSI: registration + re-exports."""

from strategies.inverse_fisher_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Inverse Fisher RSI",
        slug="inverse_fisher_rsi",
        description=(
            "John Ehlers' Inverse Fisher Transform on a 5-bar RSI: value1 = 0.1*(RSI-50), smoothed by a 9-bar weighted average, then compressed to (-1, +1) by (e^2v-1)/(e^2v+1). Long when the transform crosses above -0.5, short below +0.5. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Inverse Fisher Transform (John Ehlers)",
        source_url="https://c.mql5.com/forextsd/forum/59/the_inverse_fisher_transform.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
