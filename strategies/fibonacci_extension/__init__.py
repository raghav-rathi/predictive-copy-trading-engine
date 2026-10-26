"""Fibonacci Retracement Entry: registration + re-exports."""

from strategies.fibonacci_extension import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fibonacci Retracement Entry",
        slug="fibonacci_extension",
        description=(
            "Fibonacci retracement entry: in a SMA50 trend, enter on a turn back from the 38.2–61.8% retracement zone of the last 50-bar range; exit on a SMA50 cross."
        ),
        source_name="Fibonacci retracement (Murphy; Edwards & Magee retracement levels)",
        source_url="https://www.investopedia.com/terms/f/fibonacciretracement.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
