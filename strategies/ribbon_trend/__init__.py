"""Ribbon-trend engine: registration + re-exports."""

from strategies.ribbon_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EMA ribbon (8/13/21/34/55) alignment trend system",
        slug="ribbon_trend",
        description=(
            "Enter when the 8/13/21/34/55 EMA ribbon flips to full "
            "alignment with >0.4% fan spread; exit when alignment breaks "
            "or the fan compresses below 0.2%."
        ),
        source_name="Multi-EMA ribbon alignment (trend-following classic)",
        source_url="https://www.investopedia.com/terms/e/exponential-moving-average.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
