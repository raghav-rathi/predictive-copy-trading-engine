"""Sperandeo 2B false-breakout reversal: registration + re-exports."""

from strategies.sperandeo_2b import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Sperandeo 2B False-Breakout Reversal",
        slug="sperandeo_2b",
        description="Victor Sperandeo's 2B: a new 20-bar high/low, a pullback of at least 3 bars, a breakout bar closing beyond the extreme, then a close back below the breakout bar's low (short) or above its high (long) -- the false breakout fails and price reverses. Exit on the opposite 2B pattern.",
        source_name="Victor Sperandeo — Trader Vic II: Principles of Professional Speculation (2B pattern)",
        source_url="https://roboforex.com/blog/education/trading-like-sperandeo-1-2-3-reversal-and-2b-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
