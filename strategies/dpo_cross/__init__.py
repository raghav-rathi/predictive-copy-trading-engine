"""DPO Cross: registration + re-exports."""

from strategies.dpo_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DPO Cross",
        slug="dpo_cross",
        description=(
            "Detrended Price Oscillator: close minus the 20-bar SMA displaced back 11 bars (20/2 + 1). Long on a cross above zero, short on a cross below zero, exit on the opposite cross. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Detrended Price Oscillator (DPO)",
        source_url="https://docs.prorealalgos.com/dpo.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
