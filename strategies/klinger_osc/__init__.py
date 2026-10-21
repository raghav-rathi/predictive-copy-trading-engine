"""Klinger Volume Oscillator engine: registration + re-exports."""

from strategies.klinger_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Klinger Volume Oscillator",
        slug="klinger_osc",
        description=(
            "Stephen Klinger's volume oscillator: volume force "
            "VF = v*(2*dm/cm-1)*trend*100 (cm = cumulative range kept "
            "per trend regime), kvo = EMA(VF,34)-EMA(VF,55) vs a "
            "13-EMA signal line; long on cross-up, short on cross-down, "
            "exits on the opposite cross; 2xATR stop, 3xATR chandelier "
            "trail, 150-bar max hold."
        ),
        source_name="Klinger Volume Oscillator (Stephen Klinger)",
        source_url="https://www.lumleytrading.com/klinger-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
