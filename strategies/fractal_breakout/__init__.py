"""Bill Williams fractal breakout engine: registration + re-exports."""

from strategies.fractal_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fractal Breakout (Bill Williams)",
        slug="fractal_breakout",
        description=(
            "5-bar Bill Williams fractals (2 each side, confirmed 2 bars "
            "late, levels forward-filled); long on close crossing above "
            "the last confirmed up-fractal level with close > SMA200 "
            "(Alligator substitute), short mirror; exits on a cross back "
            "across the fractal level or an opposing fractal break; "
            "2xATR stop, 80-bar max hold."
        ),
        source_name="Aron Groups, Bill Williams Indicators (fractals)",
        source_url="https://arongroups.co/technical-analyze/bill-williams-indicators/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
