"""Choppiness-regime engine: registration + re-exports."""

from strategies.choppiness import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dreiss Choppiness-regime Donchian system",
        slug="choppiness",
        description=(
            "CHOP(14) regime filter (trend < 38.2, chop > 61.8); Donchian(20) "
            "breakouts only in trending regimes; exit on regime flip to "
            "chop or a midline cross."
        ),
        source_name="E.W. Dreiss — Choppiness Index",
        source_url="https://www.investopedia.com/terms/c/choppiness-index.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
