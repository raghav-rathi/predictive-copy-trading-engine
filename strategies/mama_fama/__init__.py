"""Ehlers MAMA/FAMA cross engine: registration + re-exports."""

from strategies.mama_fama import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers MAMA/FAMA Cross",
        slug="mama_fama",
        description=(
            "John Ehlers' MESA Adaptive Moving Average: a Hilbert-transform "
            "discriminator measures the dominant cycle period each bar and "
            "adapts the smoothing alpha (fast_limit 0.5 when the cycle "
            "shortens, down to slow_limit 0.05 when it lengthens). Long on "
            "MAMA crossing above FAMA with close above MAMA; short on the "
            "mirror; exits on the opposite cross; 2xATR stop, 200-bar max "
            "hold."
        ),
        source_name="Ehlers MAMA (prorealcode.com, from Ehlers' original code)",
        source_url="https://www.prorealcode.com/prorealtime-indicators/john-ehlers-mama-the-mother-of-adaptive-moving-average/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
