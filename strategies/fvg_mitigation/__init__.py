"""FVG Mitigation: registration + re-exports."""

from strategies.fvg_mitigation import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="FVG Mitigation",
        slug="fvg_mitigation",
        description=(
            "Smart Money Concepts fair value gaps: a three-bar imbalance where bar 3's low clears bar 1's high (bullish) or bar 3's high clears bar 1's low (bearish). Enter on the first retracement into the most recent unfilled gap, exit when price closes through the gap. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Fair Value Gap (SMC / ICT)",
        source_url="https://www.trade-ideas.com/learning-center/trading-strategies/fair-value-gap-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
