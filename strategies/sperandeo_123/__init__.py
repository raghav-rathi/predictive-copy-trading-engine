"""Victor Sperandeo 1-2-3 engine: registration + re-exports."""

from strategies.sperandeo_123 import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="1-2-3 Trend Change (Sperandeo)",
        slug="sperandeo_123",
        description=(
            "Trader Vic 1-2-3 reversal: trend-line break (5-bar fractal "
            "pivots, 200-bar lookback), failed retest pivot, entry on a "
            "close through the interim swing extreme; opposite pattern "
            "reverses; 1.5xATR stop (point-2 proxy), 3xATR target (2R), "
            "72-bar max hold."
        ),
        source_name="Victor Sperandeo, Trader Vic: Methods of a Wall Street Master",
        source_url="https://roboforex.com/blog/education/trading-like-sperandeo-1-2-3-reversal-and-2b-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
