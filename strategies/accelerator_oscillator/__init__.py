"""Accelerator Oscillator (Bill Williams) engine: registration + re-exports."""

from strategies.accelerator_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Accelerator Oscillator",
        slug="accelerator_oscillator",
        description=(
            "Accelerator Oscillator (Bill Williams): med = (h+l)/2, "
            "ao = SMA(med,5) - SMA(med,34), ac = ao - SMA(ao,5); long "
            "when ac>0 with 2 green bars or ac<0 with 3 green bars, "
            "short symmetric; exits on the opposite entry condition "
            "or 2 bars of the against color; 2xATR stop, 2.5xATR trail, "
            "120-bar max hold."
        ),
        source_name="Accelerator Oscillator (Bill Williams, New Trading Dimensions)",
        source_url="https://www.gate.com/learn/articles/accelerator-oscillator-vs-awesome-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
