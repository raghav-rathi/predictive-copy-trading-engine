"""DEMA Crossover: registration + re-exports."""

from strategies.dema_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DEMA Crossover",
        slug="dema_cross",
        description="Patrick Mulloy's Double Exponential Moving Average crossover (1994): DEMA(n) = 2*EMA(n) - EMA(EMA(n)). Long when fast DEMA(12) crosses above slow DEMA(26); short on the cross below; exit on the reverse cross.",
        source_name="Patrick Mulloy DEMA (1994)",
        source_url="https://www.tickatlas.com/learn/indicators/dema",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
