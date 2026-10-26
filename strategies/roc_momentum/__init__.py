"""ROC Momentum: registration + re-exports."""

from strategies.roc_momentum import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ROC Momentum",
        slug="roc_momentum",
        description=(
            "Rate of change (12) zero-line crossover: long on a cross above zero, short on a cross below, exit on the opposite cross."
        ),
        source_name="Rate of Change (Murphy, Technical Analysis of the Financial Markets)",
        source_url="https://www.investopedia.com/terms/r/rateofchange.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
