"""Williams fractal breakout + Alligator filter: registration + re-exports."""

from strategies.williams_fractals import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Williams Fractal Breakout",
        slug="williams_fractals",
        description="Bill Williams fractal breakout with an Alligator filter: a 5-bar fractal (middle bar's high highest vs 2 bars each side, confirmed 2 bars late) sets the breakout level; long when the close crosses above the most recent up-fractal high while price is above the Alligator teeth and lips > teeth > jaw (awake, pointing up); short is the mirror; exit on the reverse fractal break. Alligator lines are SMMA(13/8/5) of median price, used unshifted.",
        source_name="Fractals gold trading (pro-scalper.com)",
        source_url="https://www.pro-scalper.com/indicators/fractals-gold-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
