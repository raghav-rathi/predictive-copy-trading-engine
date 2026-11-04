"""Stochastic + MACD Combo: registration + re-exports."""

from strategies.stoch_macd_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic + MACD Combo",
        slug="stoch_macd_combo",
        description="Stochastic(14,3) + MACD(12,26,9) confirmation combo: long on a %K cross above %D while %K is under 30 (oversold) and MACD sits above its signal line; short on a %K cross below %D while %K is over 70 and MACD sits below its signal line; exit on the opposite %K/%D cross.",
        source_name="Stochastic + MACD confirmation combo",
        source_url="https://roboforex.com/blog/education/efficient-strategies-based-on-stochastic-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
