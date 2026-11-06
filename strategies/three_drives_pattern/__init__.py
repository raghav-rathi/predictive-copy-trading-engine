"""Three Drives Pattern: registration + re-exports."""

from strategies.three_drives_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Three Drives Pattern",
        slug="three_drives_pattern",
        description="Three Drives harmonic pattern: three successive lower pivot lows with pullbacks retracing 0.618/0.786 of the prior drive and each new drive extending 1.272/1.618 of the prior pullback, symmetric drive lengths; enter long on reversal confirmation after D3 and exit at the 61.8% retracement of the full move; bearish mirror.",
        source_name="Three Drives harmonic pattern",
        source_url="https://www.luxalgo.com/library/concept/three-drives/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
