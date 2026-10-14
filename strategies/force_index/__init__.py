"""Force Index engine: registration + re-exports."""

from strategies.force_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Force Index pullback (FI13 trend / FI2 trigger)",
        slug="force_index",
        description=(
            "Long FI13>0 dips of FI2 below zero, short FI13<0 pops of FI2 "
            "above zero; exit on FI13 flip or FI2 hook against the position; "
            "2.5xATR(14) stop."
        ),
        source_name="Alexander Elder, Trading for a Living (Wiley, 1993)",
        source_url="https://www.multicharts.com/support/base/oscillators-gt-force-index/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
