"""Wilder Volatility System: registration + re-exports."""

from strategies.wilder_volatility_system import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder Volatility System",
        slug="wilder_volatility_system",
        description="J. Welles Wilder Volatility System (1978): long when the close breaks above the previous bar's high + ATR(7), short below the previous bar's low - ATR(7); exit/reverse on the opposite trigger, with the harness stop/trail as the exit mechanism.",
        source_name="J. Welles Wilder — Volatility System, New Concepts in Technical Trading Systems (1978)",
        source_url="https://www.investopedia.com/terms/v/volatility-system.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
