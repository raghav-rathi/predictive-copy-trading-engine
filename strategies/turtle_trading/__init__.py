"""Turtle Trading: registration + re-exports."""

from strategies.turtle_trading import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Turtle Trading",
        slug="turtle_trading",
        description="The Original Turtle Trading Rules (Curtis Faith): System 1 longs on a close above the prior 20-bar high / shorts below the prior 20-bar low, exiting on a close through the opposite 10-bar channel; System 2 uses a 55-bar entry / 20-bar exit. Either system firing enters. N = ATR(20).",
        source_name="Turtle Trading Rules (Curtis Faith)",
        source_url="https://synapsetrading.com/turtle-trading-rules/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
