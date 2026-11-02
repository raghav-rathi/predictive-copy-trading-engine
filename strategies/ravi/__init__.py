"""RAVI: registration + re-exports."""

from strategies.ravi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RAVI",
        slug="ravi",
        description=(
            "Chande Range Action Verification Index: 100*(SMA(7)-SMA(65))/SMA(65); long on cross above +0.3%, short below -0.3%, exit on reversion to zero."
        ),
        source_name="Range Action Verification Index (Tushar Chande)",
        source_url="https://www.definedgesecurities.com/library/ravi/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
