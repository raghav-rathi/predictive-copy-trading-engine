"""KAMA cross engine: registration + re-exports."""

from strategies.kama_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="KAMA Cross",
        slug="kama_cross",
        description=(
            "Perry Kaufman KAMA cross (Smarter Trading, 1995): fast "
            "KAMA(ER 10, fast 2, slow 30) vs slow KAMA(ER 20, fast 2, "
            "slow 30); long when the fast crosses above the slow, "
            "short when it crosses below, exit on the opposite cross; "
            "2xATR stop, 3xATR trail, 60-bar max hold."
        ),
        source_name='Perry Kaufman, "Smarter Trading" (1995) — KAMA',
        source_url="https://docs.wickra.org/Indicators/Indicator-Kama",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
