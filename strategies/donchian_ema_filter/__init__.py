"""Donchian EMA Filter: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.donchian_ema_filter import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian EMA Filter",
        slug="donchian_ema_filter",
        description="Richard Donchian / Turtle System 1: long on a close above the prior 20-bar high while above EMA(50), short on a close below the prior 20-bar low while below EMA(50); exit long on a close below the prior 10-bar low and short on a close above the prior 10-bar high, plus the harness stop/trail.",
        source_name="Donchian Channel (PatternsWizard)",
        source_url="https://patternswizard.com/donchian-channel/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
