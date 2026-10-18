"""Wilder Swing Index / ASI engine: registration + re-exports."""

from strategies.wilder_swing_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder Swing Index / ASI",
        slug="wilder_swing_index",
        description=(
            "Wilder's Swing Index per bar, ASI = cumulative SI; long on ASI "
            "breakout above its prior 20-bar high, short below the prior "
            "20-bar low, exit on the opposite break; 2xATR stop, 48-bar max "
            "hold."
        ),
        source_name="J. Welles Wilder — Swing Index / ASI (New Concepts in Technical Trading Systems, 1978)",
        source_url="https://efs.kb.esignal.com/hc/en-us/articles/6362864171547-Accumulation-Swing-Index-ASI",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
