"""George Lane Slow Stochastic: registration + re-exports."""

from strategies.slow_stochastic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Slow Stochastic",
        slug="slow_stochastic",
        description=(
            "George Lane's Slow Stochastic on 1h bars. %K = 100*(c - "
            "lowest low 14)/(highest high 14 - lowest low 14); %D = "
            "SMA(3) of %K. LONG on %K crossing above %D while %K < 20; "
            "SHORT on %K crossing below %D while %K > 80. Exit on the "
            "opposite cross. 1.5xATR stop, 2xATR chandelier trail, "
            "72-bar (~3-day) max hold."
        ),
        source_name="George Lane Slow Stochastic (StockCharts Stochastic Oscillator)",
        source_url="https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:stochastic_oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
