"""Rising / Falling Three Methods: registration + re-exports."""

from strategies.three_methods_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Rising / Falling Three Methods",
        slug="three_methods_pattern",
        description=(
            "Nison rising/falling three methods (5 bars): a strong candle, three small counter-trend candles contained inside its range, then a strong candle closing beyond the first candle's close; entry on the fifth candle's close."
        ),
        source_name="Steve Nison three methods (Japanese Candlestick Charting Techniques)",
        source_url="https://www.investopedia.com/terms/t/three_white_soldiers.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
