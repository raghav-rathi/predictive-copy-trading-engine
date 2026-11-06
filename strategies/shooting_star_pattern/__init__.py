"""Shooting Star Pattern: registration + re-exports."""

from strategies.shooting_star_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Shooting Star Pattern",
        slug="shooting_star_pattern",
        description="Steve Nison shooting star / inverted hammer: short on a shooting star (small body in the lower third, upper shadow >= 2x body, lower shadow <= 10% of range) in an uptrend (close above EMA(20), 5-bar return > +1%); long on the inverted-hammer mirror in a downtrend. Exits on the opposite pattern.",
        source_name="Steve Nison shooting star (Japanese Candlestick Charting Techniques, 1991)",
        source_url="https://www.quantum-algo.com/blog/guides/shooting-star-pattern-complete-guide/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
