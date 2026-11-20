"""Bollinger Bands %b mean reversion: registration + re-exports."""

from strategies.bollinger_reversion import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger Bands %b Mean Reversion",
        slug="bollinger_reversion",
        description="Bollinger Bands(20, 2.0) %b mean reversion: long on a close below the lower band (tag), exit on a close back at/above the middle band (SMA(20)); short on a close above the upper band, exit on a close back at/below the middle band. No extra filter — the band tag is the signal; plus the harness stop/trail.",
        source_name="John Bollinger, Bollinger on Bollinger Bands",
        source_url="https://www.bollingerbands.com/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
