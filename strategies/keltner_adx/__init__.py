"""Keltner+ADX engine: registration + re-exports."""

from strategies.keltner_adx import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner Breakout (ADX-filtered)",
        slug="keltner_adx",
        description=(
            "Close crossing Keltner(20, 1.5) bands with ADX(14) > 25 "
            "confirmation; Keltner-mid exits; 2xATR stop + 2.5xATR trailing."
        ),
        source_name="Keltner channels + ADX (Raschke variant, public)",
        source_url="https://www.investopedia.com/terms/k/keltnerchannel.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
