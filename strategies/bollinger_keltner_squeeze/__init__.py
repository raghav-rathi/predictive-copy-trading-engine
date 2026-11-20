"""Bollinger/Keltner Squeeze: registration + re-exports."""

from strategies.bollinger_keltner_squeeze import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger/Keltner Squeeze",
        slug="bollinger_keltner_squeeze",
        description="John Carter TTM Squeeze: Bollinger Bands (20, 2) vs Keltner Channels (20, 1.5xATR(14)); the squeeze is ON while the bands sit inside the channels. Fire is the first bar the squeeze turns OFF after being ON; long on fire with positive TTM momentum, short on fire with negative momentum; exit on the opposite signal, plus the harness stop/trail.",
        source_name="John Carter TTM Squeeze (PatternsWizard / TrendSpider)",
        source_url="https://patternswizard.com/ttm-squeeze-indicator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
