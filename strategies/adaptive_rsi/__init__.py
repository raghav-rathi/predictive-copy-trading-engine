"""Adaptive RSI: registration + re-exports."""

from strategies.adaptive_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Adaptive RSI",
        slug="adaptive_rsi",
        description=(
            "Kaufman efficiency-ratio adaptive RSI: RSI(14) smoothed with a Kaufman AMA whose speed follows the 10-bar efficiency ratio; long on cross above 30, short below 70, exit at 50."
        ),
        source_name="Kaufman Adaptive Moving Average (Perry Kaufman)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:kaufman_adaptive_moving_average",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
