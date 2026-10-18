"""Ehlers Cyber Cycle engine: registration + re-exports."""

from strategies.ehlers_cyber_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Cyber Cycle (Ehlers)",
        slug="ehlers_cyber_cycle",
        description=(
            "Ehlers Cyber Cycle (alpha=0.07) of (h+l)/2; entries on the "
            "cycle crossing its 1-bar trigger; exits on the opposite "
            "cross; 2xATR stop, 20-bar max hold."
        ),
        source_name="John Ehlers, Cybernetic Analysis for Stocks and Futures — MQL5 code article",
        source_url="https://www.mql5.com/en/articles/288",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
