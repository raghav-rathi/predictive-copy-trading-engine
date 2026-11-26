"""Donchian Stochastic engine: registration + re-exports."""

from strategies.donchian_stochastic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian Stochastic",
        slug="donchian_stochastic",
        description=(
            "Richard Donchian channel breakout + Stochastic(14,3,3) filter: long on a close above the prior 20-bar Donchian high with %K above %D and below 80, short on a close below the prior 20-bar low with %K below %D and above 20; Turtle exit on the 10-bar channel or a %K/%D cross against the position; 2xATR stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="Richard Donchian — Donchian channel (Wikipedia)",
        source_url="https://en.wikipedia.org/wiki/Donchian_channel",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
