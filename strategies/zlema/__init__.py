"""Zero Lag EMA: registration + re-exports."""

from strategies.zlema import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Zero Lag EMA",
        slug="zlema",
        description="Zero Lag EMA cross ZLEMA(20) vs ZLEMA(50): long when the fast ZLEMA crosses above the slow ZLEMA; short when it crosses below; exit on the opposite cross.",
        source_name="Zero Lag EMA (John Ehlers & Ric Way, 2010)",
        source_url="https://www.luxalgo.com/library/concept/zlema/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
