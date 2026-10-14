"""Klinger Volume Oscillator engine: registration + re-exports."""

from strategies.klinger_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Klinger Volume Oscillator signal-line system",
        slug="klinger_oscillator",
        description=(
            "KVO = EMA(34)-EMA(55) of signed volume force; long when it "
            "crosses above its 13-EMA signal, short on the mirror; exit on "
            "the opposite cross."
        ),
        source_name="Stephen Klinger — Klinger Volume Oscillator (S&C, 1997)",
        source_url="https://library.tradingtechnologies.com/trade/chrt-ti-klinger-volume-oscillator.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
