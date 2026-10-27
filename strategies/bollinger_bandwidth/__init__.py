"""Bollinger Bandwidth Breakout: registration + re-exports."""

from strategies.bollinger_bandwidth import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger Bandwidth Breakout",
        slug="bollinger_bandwidth",
        description=(
            "Bollinger Bandwidth (20,2): long on a close above the upper band while bandwidth is expanding above its 20-bar average; short on a close below the lower band while expanding; exit at the mid-band."
        ),
        source_name="John Bollinger Bandwidth / %B family (Bollinger on Bollinger Bands)",
        source_url="https://www.investopedia.com/terms/b/bollingerbands.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
