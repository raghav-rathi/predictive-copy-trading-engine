"""Chandelier Exit engine: registration + re-exports."""

from strategies.chandelier_exit import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chandelier Exit (LeBeau trend system)",
        slug="chandelier_exit",
        description=(
            "Enter on 22-bar high/low breakout; exit at the chandelier "
            "line HH22-3xATR / LL22+3xATR."
        ),
        source_name="Chandelier Exit (Chuck LeBeau) — tradingview-strategies README",
        source_url="https://github.com/eternahybridexchange/tradingview-strategies/blob/HEAD/strategies/trend-following/chandelier-exit/README.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
