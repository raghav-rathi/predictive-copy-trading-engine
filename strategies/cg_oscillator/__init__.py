"""CG Oscillator: registration + re-exports."""

from strategies.cg_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="CG Oscillator",
        slug="cg_oscillator",
        description=(
            "John Ehlers' Center of Gravity oscillator: the deviation of the price-weighted centroid of the last 10 closes from the window midpoint, against its 3-bar SMA trigger line. Long on the CG cross above its trigger, short below. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Center of Gravity Oscillator (John Ehlers)",
        source_url="https://admiralmarkets.com/education/articles/forex-indicators/trading-with-the-center-of-gravity-indicator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
