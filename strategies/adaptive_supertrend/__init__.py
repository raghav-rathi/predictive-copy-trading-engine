"""Adaptive Supertrend engine: registration + re-exports."""

from strategies.adaptive_supertrend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Adaptive Supertrend",
        slug="adaptive_supertrend",
        description=(
            "Supertrend (Seban) with a Choppiness-Index-adaptive ATR "
            "multiplier: ATR(10), CHOP(14); k=2.0 when chop<38 "
            "(trending), k=4.0 when chop>62 (choppy), else k=3.0; "
            "long on a supertrend flip to up, short on a flip to down; "
            "exit on the opposite flip; 2xATR stop, 3xATR trail, "
            "200-bar max hold."
        ),
        source_name="Supertrend (Olivier Seban) + Choppiness Index (E.W. Dreiss)",
        source_url="https://www.investopedia.com/supertrend-indicator-7976167",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
