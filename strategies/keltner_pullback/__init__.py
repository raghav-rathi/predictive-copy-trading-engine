"""Keltner pullback: registration + re-exports."""

from strategies.keltner_pullback import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner Pullback",
        slug="keltner_pullback",
        description=(
            "Keltner-channel trend pullback: in an EMA50 uptrend "
            "(close above a rising EMA50), enter long when price "
            "crosses back above the Keltner midline (EMA20) after "
            "a dip to/through it; bearish mirror. Distinct from "
            "keltner_adx, keltner_rsi and keltner_squeeze, which "
            "trade band breakouts or squeezes, not midline "
            "pullbacks. Exit on the opposite midline cross. "
            "2xATR stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="Keltner channels (Chester Keltner; StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/keltner-channels",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
