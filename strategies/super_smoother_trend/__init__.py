"""Ehlers SuperSmoother trend crossover engine: registration + re-exports."""

from strategies.super_smoother_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SuperSmoother Trend",
        slug="super_smoother_trend",
        description=(
            "Ehlers SuperSmoother trend crossover: long when the fast "
            "SuperSmoother(10) crosses above the slow SuperSmoother(30), "
            "short when it crosses below; exit on the opposite cross; "
            "2xATR stop, 3xATR chandelier trail, 60-bar max hold."
        ),
        source_name='John F. Ehlers, "Cybernetic Analysis for Stocks and Futures" (2004) — SuperSmoother',
        source_url="https://www.mesasoftware.com/papers/UltimateSmoother.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
