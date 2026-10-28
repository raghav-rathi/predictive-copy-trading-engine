"""PPO signal-line cross: registration + re-exports."""

from strategies.ppo_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="PPO Signal Cross",
        slug="ppo_cross",
        description="Percentage Price Oscillator PPO=(EMA12-EMA26)/EMA26*100 crosses above its EMA(9) signal = long, below = short; exit on the opposite cross. 2xATR stop, 2.5xATR trail, 168-bar max hold.",
        source_name="Percentage Price Oscillator (StockCharts ChartSchool)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
