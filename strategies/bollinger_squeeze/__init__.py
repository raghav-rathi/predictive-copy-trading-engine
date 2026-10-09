"""Bollinger squeeze engine: registration + re-exports."""

from strategies.bollinger_squeeze import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger Squeeze Expansion (TTM-style)",
        slug="bollinger_squeeze",
        description=(
            "BB(20,2) inside Keltner(20,1.5) = squeeze; enter on release in "
            "the momentum direction; 1.5xATR stop, 3xATR target, 72-bar cap."
        ),
        source_name="John Carter TTM Squeeze (public mechanics)",
        source_url="https://www.simplertrading.com/ttm-squeeze-indicator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
