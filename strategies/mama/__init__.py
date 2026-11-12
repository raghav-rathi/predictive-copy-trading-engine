"""MAMA engine: registration + re-exports."""

from strategies.mama import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MAMA",
        slug="mama",
        description="John F. Ehlers MESA Adaptive Moving Average (TASC, Sep 2001; Cybernetic Analysis for Stocks and Futures, 2004): Hilbert-transform phase rate of change sets the adaptive alpha (FastLimit 0.5 / SlowLimit 0.05); long when MAMA crosses above FAMA, short on a cross below, exit on the opposite cross.",
        source_name="John F. Ehlers — MAMA, MESA Adaptive Moving Average (TASC, Sep 2001)",
        source_url="https://docs.wickra.org/Indicators/Indicator-Mama",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
