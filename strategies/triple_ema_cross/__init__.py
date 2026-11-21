"""Triple EMA Crossover: registration + re-exports."""

from strategies.triple_ema_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Triple EMA Crossover",
        slug="triple_ema_cross",
        description="Triple moving-average crossover: EMA(5) crossing EMA(13) is the trigger, filtered by the EMA(50) trend stack — long only when EMA5 > EMA13 > EMA50, short only when EMA5 < EMA13 < EMA50; exits on the EMA(5)/EMA(13) cross back, plus the harness stop/trail.",
        source_name="Triple Moving Average Crossover (HowToTrade)",
        source_url="https://howtotrade.com/trading-strategies/triple-moving-average-crossover/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
