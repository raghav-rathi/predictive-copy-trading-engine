"""Diamond top/bottom reversal: registration + re-exports."""

from strategies.diamond_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Diamond Pattern",
        slug="diamond_pattern",
        description=(
            "Classic diamond top/bottom reversal: a 5+ bar expanding "
            "range phase (highs rising, lows falling) followed by a 5+ "
            "bar contracting range phase (highs falling, lows rising), "
            "total pattern 15-40 bars, broken by a close beyond the "
            "converging range boundary on volume above 1.2x the pattern "
            "average. Exit on the opposite breakout. 2xATR stop, 2.5xATR "
            "trail, 168-bar max hold."
        ),
        source_name="Diamond top/bottom reversal (Edwards & Magee, Technical Analysis of Stock Trends)",
        source_url="https://www.investopedia.com/terms/d/diamondtop.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
