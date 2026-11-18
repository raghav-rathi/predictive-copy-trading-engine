"""Volatility Contraction Pattern (VCP): registration + re-exports."""

from strategies.vcp import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volatility Contraction Pattern",
        slug="vcp",
        description="Volatility Contraction Pattern (Minervini): long a Stage-2 uptrend when >=2 successive pullbacks shrink (each shallower, higher trough, drying volume) and the close breaks above the last contraction's pivot high on expanding volume; short is the symmetric mirror; exit on a failed breakout back through the pivot or the opposite signal, plus the harness stop/trail.",
        source_name="Quantum Algo VCP Pattern guide; TradePiko VCP Pattern",
        source_url="https://www.quantum-algo.com/blog/guides/vcp-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
