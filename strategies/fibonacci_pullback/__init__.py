"""Fibonacci pullback-entry engine: registration + re-exports."""

from strategies.fibonacci_pullback import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fibonacci Pullback Entry",
        slug="fibonacci_pullback",
        description=(
            "SMA200 trend filter + trailing 60-bar swing high/low; long "
            "when the low dips to/below the 50% retracement, holds above "
            "78.6%, and closes back above 61.8%; short mirror on the "
            "38.2-50% bounce zone; exits at the prior swing high/low; "
            "2xATR stop, 100-bar max hold."
        ),
        source_name="FinancialTechWiz, Fibonacci Retracement (TradingView)",
        source_url="https://www.financialtechwiz.com/post/fibonacci-retracement-tradingview/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
