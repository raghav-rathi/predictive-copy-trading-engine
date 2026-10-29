"""RSI failure-swing: registration + re-exports."""

from strategies.rsi_failure_swing import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI Failure Swing",
        slug="rsi_failure_swing",
        description=(
            "Cardwell/Wilder RSI(14) failure swings: bullish when RSI "
            "dips below 30, rallies, pulls back to a higher swing low, "
            "then breaks above the intervening swing high; bearish "
            "mirror above 70. Pure RSI structure -- no price "
            "comparison, unlike rsi_divergence. Pivots lagged by 2 "
            "bars (no lookahead). Exit on the opposite swing. "
            "2xATR stop, 2.5xATR trail, 168-bar max hold."
        ),
        source_name="RSI failure swings (Wilder; Cardwell RSI range rules, StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
