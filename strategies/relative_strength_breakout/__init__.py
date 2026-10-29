"""Relative-strength ratio-line breakout: registration + re-exports.

SPEC uses the standard single-frame path: add_indicators loads
the BTC benchmark from the shipped cache when no benchmark
frame is passed (see indicators.py for the sourcing order and
the deliberate no-proxy rule). For BTC itself the ratio is 1
by construction and no trade fires.
"""

from strategies.relative_strength_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Relative Strength Breakout",
        slug="relative_strength_breakout",
        description=(
            "Coin/BTC relative-strength ratio-line breakout: long "
            "when the coin/BTC ratio breaks above its prior 20-bar "
            "high, short below its prior 20-bar low; exit on a fade "
            "back through the ratio's 20-bar mean. BTC benchmark "
            "from the shipped cache (or an explicit benchmark "
            "frame). 2xATR stop, 2.5xATR trail, 168-bar max hold."
        ),
        source_name="Relative strength ratio line (Mansfield relative strength; Investopedia)",
        source_url="https://www.investopedia.com/terms/r/relativestrength.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
