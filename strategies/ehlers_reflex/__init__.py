"""Reflex Zero-Lag: registration + re-exports."""

from strategies.ehlers_reflex import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Reflex Zero-Lag",
        slug="ehlers_reflex",
        description=(
            "Reflex (Ehlers): 2-pole SuperSmoother(20) of close, "
            "detrended by linear extrapolation over the lookback, "
            "normalized by its own variance EMA; long on a zero "
            "cross up, short on a zero cross down; exits on the "
            "opposite cross; 2xATR stop, 2.5xATR chandelier trail, "
            "150-bar max hold."
        ),
        source_name="Reflex (John Ehlers, TASC Feb 2020)",
        source_url="https://forex-station.com/download/file.php?id=3357914&sid=f0c366b7fa15f05758951129dc3ccff7",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
