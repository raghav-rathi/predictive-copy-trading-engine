"""Alligator + Awesome Oscillator engine: registration + re-exports."""

from strategies.alligator_awesome_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Alligator + Awesome Oscillator Combo",
        slug="alligator_awesome_combo",
        description=(
            "Bill Williams Profitunity: Alligator SMMA "
            "(Jaw 13 / Teeth 8 / Lips 5, unshifted) + Awesome "
            "Oscillator SMA(5)-SMA(34) of median price + "
            "2-bar fractals. Long on a close crossing above a "
            "confirmed up-fractal high (above the teeth) with "
            "AO > 0 and rising and lips > teeth > jaw; short "
            "mirror. Exit on close back inside the lips, 2 "
            "consecutive AO bars against the trade, or the "
            "opposite entry; 2xATR stop, 3xATR trail, 120-bar "
            "max hold."
        ),
        source_name="Bill Williams Profitunity / Trading Chaos (MQL5)",
        source_url="https://www.mql5.com/en/articles/16365",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
