"""Percentage Price Oscillator engine: registration + re-exports."""

from strategies.ppo_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Percentage Price Oscillator",
        slug="ppo_oscillator",
        description=(
            "StockCharts Percentage Price Oscillator (Gerald Appel "
            "lineage): PPO = 100*(EMA(12)-EMA(26))/EMA(26) with a "
            "9-period EMA signal line; long on a signal-line cross "
            "up while PPO > 0, short on a cross down while PPO < 0, "
            "exit on the opposite cross; 2xATR stop, 3xATR trail, "
            "60-bar max hold."
        ),
        source_name='StockCharts ChartSchool, "Percentage Price Oscillator"',
        source_url="https://chartschool.stockcharts.com/~gitbook/pdf?page=9QwAOEXf9dmW4Fkyz4Yb&only=yes&limit=100",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
