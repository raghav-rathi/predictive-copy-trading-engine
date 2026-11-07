"""1-2-3 Reversal: registration + re-exports."""

from strategies.one_two_three_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="1-2-3 Reversal",
        slug="one_two_three_reversal",
        description="Joe Ross 1-2-3 reversal on 5-bar fractal pivots: point 1 is the fractal low ending a decline, point 2 the high of the first rally off point 1 (leg >= 1.0x ATR(14)), point 3 a pullback low holding above point 1; complete on a close above point 2 to go long, exit on a close below point 3 or an opposite 1-2-3 completion; bearish mirror.",
        source_name="Joe Ross 1-2-3 reversal (LuxAlgo concept library)",
        source_url="https://www.luxalgo.com/library/concept/1-2-3-reversal/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
