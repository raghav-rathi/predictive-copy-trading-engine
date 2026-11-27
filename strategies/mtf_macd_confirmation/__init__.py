"""Multi-Timeframe MACD Confirmation engine: registration + re-exports."""

from strategies.mtf_macd_confirmation import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Multi-Timeframe MACD Confirmation",
        slug="mtf_macd_confirmation",
        description=(
            "Elder Triple Screen: trade 1h MACD(12, 26, 9) signal-line "
            "crosses only in the direction of the 4h MACD trend "
            "(4h histogram > 0 for longs, < 0 for shorts); exit on "
            "the 1h cross back or the 4h histogram crossing zero; "
            "2xATR stop, 3xATR trail, 168-bar max hold."
        ),
        source_name="Quantpedia — How to Design a Simple Multi-Timeframe Trend Strategy on Bitcoin",
        source_url="https://quantpedia.com/how-to-design-a-simple-multi-timeframe-trend-strategy-on-bitcoin/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
