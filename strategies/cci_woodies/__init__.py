"""Woodies CCI engine: registration + re-exports."""

from strategies.cci_woodies import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Woodies CCI hook system",
        slug="cci_woodies",
        description=(
            "CCI(14); long when CCI crosses above 0 after a hook below "
            "-100 within 20 bars; short on the mirror; exit on CCI "
            "crossing back through 0."
        ),
        source_name="Ken Wood — Woodies CCI system",
        source_url="https://www.investopedia.com/terms/c/cci.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
