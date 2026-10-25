"""Swing support / resistance bounce: registration + re-exports."""

from strategies.swing_sr_bounce import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Swing S/R Bounce",
        slug="swing_sr_bounce",
        description=(
            "Support/resistance from clustered 5-bar zigzag pivots (levels "
            "need 2+ touches within 0.5%): long on a dip to support that "
            "closes back above it with an up close, short on the mirror at "
            "resistance; exit on a close 0.5% beyond the level or the "
            "opposite bounce. 1.5xATR stop, 2xATR trail, 72-bar max hold."
        ),
        source_name="Support / resistance bounce (Murphy, Technical Analysis of the Financial Markets)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
