"""Fast stochastic %K/%D crossover: registration + re-exports."""

from strategies.stochastics_fast import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fast Stochastic Crossover",
        slug="stochastics_fast",
        description="Fast stochastic %K(14)/%D(3) crossover with SMA(200) trend filter: long on a %K cross above %D while %K < 20 and close above SMA(200), short on a %K cross below %D while %K > 80 and close below SMA(200); exit on the opposite cross or on %K leaving the extreme zone.",
        source_name="MarketInOut — Stochastic Oscillator: Fast, Slow and Full Explained",
        source_url="https://www.marketinout.com/technical-analysis/stochastic-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
