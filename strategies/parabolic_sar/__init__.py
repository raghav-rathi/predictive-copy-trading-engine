"""Parabolic SAR engine: registration + re-exports."""

from strategies.parabolic_sar import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Parabolic SAR stop-and-reverse (Wilder)",
        slug="parabolic_sar",
        description=(
            "Wilder SAR (AF 0.02->0.20): flip long when SAR drops below "
            "price, flip short when it rises above; SAR is the trailing "
            "stop. 3xATR safety stop, 40-bar warmup, both sides."
        ),
        source_name="Parabolic SAR (J. Welles Wilder Jr.) — Disfold glossary",
        source_url="https://blog.disfold.com/glossary/parabolic-sar/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
