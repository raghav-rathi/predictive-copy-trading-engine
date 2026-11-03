"""Relative Volatility Index: registration + re-exports."""

from strategies.relative_volatility_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Relative Volatility Index",
        slug="relative_volatility_index",
        description=(
            "Donald Dorsey Relative Volatility Index (10/10): volatility-weighted RSI — standard deviation of closes split into up/down buckets. Long on cross above 50, short on cross below 50; exits on the opposite cross."
        ),
        source_name="Relative Volatility Index (Donald Dorsey)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:relative_volatility_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
