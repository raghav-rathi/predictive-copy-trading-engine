"""McClellan Oscillator engine: registration + re-exports."""

from strategies.mcclellan_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="McClellan Oscillator",
        slug="mcclellan_oscillator",
        description=(
            "Breadth oscillator on a single-asset candle-count proxy: "
            "RANA = 1000*(up-down)/(up+down) over 24 bars, oscillator = "
            "EMA19(RANA) - EMA39(RANA), summation index = cumulative "
            "oscillator. Long on a cross above 0 after a sub -50 "
            "excursion with a rising summation index; short mirrored. "
            "Exit on a cross back through 0 or the summation index "
            "turning; 1.5xATR stop, 2.5xATR target, 48-bar max hold."
        ),
        source_name="McClellan Oscillator (AAII)",
        source_url="https://www.aaii.com/journal/article/347760-looking-beyond-price-trends-with-the-mcclellan-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
