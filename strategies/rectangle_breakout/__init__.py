"""Rectangle consolidation breakout: registration + re-exports."""

from strategies.rectangle_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Rectangle Breakout",
        slug="rectangle_breakout",
        description=(
            "Classic rectangle consolidation breakout: a 20-bar range "
            "narrower than 4% of price, held tight for at least 15 bars, "
            "broken by a close beyond the range boundary on volume above "
            "1.2x the 20-bar average. Long above the range high, short "
            "below the range low; exit on a cross back through the "
            "opposite boundary or the opposite breakout. 2xATR stop, "
            "2.5xATR trail, 168-bar max hold."
        ),
        source_name="Rectangle consolidation breakout (Edwards & Magee, Technical Analysis of Stock Trends)",
        source_url="https://www.investopedia.com/terms/r/rectangle.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
