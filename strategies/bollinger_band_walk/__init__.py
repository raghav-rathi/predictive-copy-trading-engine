"""Bollinger Band Walk: registration + re-exports."""

from strategies.bollinger_band_walk import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger Band Walk",
        slug="bollinger_band_walk",
        description=(
            "Band walk: enter long on the first close above the upper Bollinger band (20,2) while the prior close was inside, short on the mirror; exit on a cross back through the middle band."
        ),
        source_name="Bollinger Bands (John Bollinger, Bollinger on Bollinger Bands)",
        source_url="https://www.investopedia.com/terms/b/bollingerbands.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
