"""MESA Sine Wave engine: registration + re-exports."""

from strategies.mesa_sine_wave import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MESA Sine Wave",
        slug="mesa_sine_wave",
        description=(
            "John Ehlers' MESA Sine Wave: Hilbert-transform "
            "in-phase/quadrature components of the detrended price, "
            "phase = atan2(Q2, I2), dominant cycle from the homodyne "
            "discriminator (clamped 6..50 bars); long when sine crosses "
            "above lead sine, short when it crosses below, exit on the "
            "opposite cross; 2xATR stop, 3xATR trail, 60-bar max hold."
        ),
        source_name='John Ehlers, "Cycle Analytics for Traders" / '
        '"Rocket Science for Traders" ch. 12',
        source_url="https://arrowalgo.com/mesa-sine-wave-complete-guide-algorithmic-trading/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
