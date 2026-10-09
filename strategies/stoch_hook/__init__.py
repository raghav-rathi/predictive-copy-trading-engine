"""Stochastic-hook engine: registration + re-exports."""

from strategies.stoch_hook import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic Hook / Anti (Raschke pullback)",
        slug="stoch_hook",
        description=(
            "Pullback entries with EMA50 bias: slowK(10) cross of trigger(4) "
            "with slowK and rawK(7) rising; exit on cross against; "
            "2xATR stop, 48-bar max hold."
        ),
        source_name="Linda Raschke, Street Smarts (Anti)",
        source_url="https://roboforex.com/blog/education/trading-strategies-that-were-a-revolution-three-strategies-of-linda-raschke/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
