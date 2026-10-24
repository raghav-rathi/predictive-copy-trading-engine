"""RSI vs its SMA signal-line cross engine: registration + re-exports."""

from strategies.rsi_ma_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI MA Cross",
        slug="rsi_ma_cross",
        description=(
            "Wilder RSI(14) vs its own SMA(14) signal line: LONG when "
            "RSI crosses above its average, SHORT when it crosses "
            "below. Exit on the opposite cross. 1.5xATR stop, 2xATR "
            "chandelier trail, 72-bar max hold."
        ),
        source_name="Relative Strength Index (Wilder, StockCharts)",
        source_url="https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:relative_strength_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
