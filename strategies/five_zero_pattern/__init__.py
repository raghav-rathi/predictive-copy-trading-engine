"""5-0 Pattern: registration + re-exports."""

from strategies.five_zero_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="5-0 Pattern",
        slug="five_zero_pattern",
        description="Scott Carney's 5-0 harmonic pattern (Harmonic Trading Vol. 2, 2007): 0-X-A-B-C pivots with AB = 1.13-1.618x XA and BC = 1.618-2.24x AB; enter long at D, the 50% retracement of BC, on reversal confirmation, and exit at the 38.2% retracement of the C-to-D leg; bearish mirror.",
        source_name="Scott Carney 5-0 pattern, Harmonic Trading Vol. 2 (2007)",
        source_url="https://roboforex.com/blog/education/how-to-trade-by-5-0-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
