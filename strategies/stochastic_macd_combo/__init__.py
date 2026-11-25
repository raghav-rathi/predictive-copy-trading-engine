"""Stochastic + MACD dual-confirmation engine: registration + re-exports."""

from strategies.stochastic_macd_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic + MACD Combo",
        slug="stochastic_macd_combo",
        description=(
            "Fast Stochastic %K(14)/%D(3) cross gated by MACD(12,26,9) "
            "histogram sign: long on an oversold %K cross up with "
            "histogram > 0, short on an overbought %K cross down "
            "with histogram < 0, exit on the opposite Stochastic "
            "cross or a histogram sign flip; 2xATR stop, 3xATR "
            "trail, 60-bar max hold."
        ),
        source_name='StockCharts ChartSchool, "Stochastic Oscillator (Fast, Slow, and Full)"',
        source_url="https://chartschool.stockcharts.com/~gitbook/pdf?page=QVB5cA3WHQlQdjo1YmxN&only=yes&limit=100",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
