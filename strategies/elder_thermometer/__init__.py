"""Elder Market Thermometer: registration + re-exports."""

from strategies.elder_thermometer import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Market Thermometer",
        slug="elder_thermometer",
        description=(
            "Elder Market Thermometer: an unusually quiet range (today's range < 60% of its 20-bar average) after a trend is the calm-before-reversal setup — long on a bullish close while price sits below its 20-bar average, short on a bearish close while above it."
        ),
        source_name="Alexander Elder Market Thermometer (Trading for a Living)",
        source_url="https://www.investopedia.com/terms/m/market-thermometer.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
