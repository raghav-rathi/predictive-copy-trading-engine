"""TRIX engine: registration + re-exports."""

from strategies.trix import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TRIX momentum system",
        slug="trix",
        description=(
            "Triple-EMA(15) rate of change; long when TRIX crosses above "
            "its 9-bar signal line below zero; short on the mirror; exit "
            "on the opposite signal cross."
        ),
        source_name="TRIX — triple exponential average momentum",
        source_url="https://www.investopedia.com/terms/t/trix.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
