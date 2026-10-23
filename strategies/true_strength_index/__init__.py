"""William Blau's True Strength Index (double-smoothed momentum oscillator).

Signal engines live in ``indicators``, ``signals`` and ``risk``; see the
README for the mechanism and the source citations.
"""

from strategies.true_strength_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="True Strength Index",
        slug="true_strength_index",
        description=(
            'William Blau\'s True Strength Index: 100 x double-smoothed momentum / double-smoothed absolute momentum (25/13) with a 7-bar signal line. Long on a signal-line cross up with TSI above zero (zero-territory filter); short mirror. Opposite-cross exits. 1.5xATR stop, 2xATR chandelier trail, 120-bar max hold.'
        ),
        source_name="True Strength Index (William Blau)",
        source_url="https://en.wikipedia.org/wiki/True_strength_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
