"""Bollinger W-bottom / M-top: registration + re-exports."""

from strategies.bollinger_w_bottom import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger W-Bottom / M-Top",
        slug="bollinger_w_bottom",
        description="John Bollinger's W-bottom / M-top: BB(20, 2.0) with %B divergence — a first low outside the lower band (%B < 0), a rally above the middle band, a second low within 1% of the first in price but with a higher %B, entered on the first close back above the middle band; exact mirror for M-tops. Exits on the close back across the middle band.",
        source_name="John Bollinger — Bollinger on Bollinger Bands (2001), W-bottoms",
        source_url="https://www.bollingerbands.com/bollinger-bands",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
