"""Ichimoku + MACD: registration + re-exports."""

from strategies.ichimoku_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ichimoku MACD",
        slug="ichimoku_macd",
        description="Ichimoku (Tenkan 9, Kijun 26, Senkou B 52, displacement 26) + MACD(12, 26, 9): long when the close is above the cloud as plotted at the bar and Tenkan crosses above Kijun with MACD histogram > 0, short on the mirror; exit on a Tenkan/Kijun cross back or the close leaving the cloud side, plus the harness stop/trail.",
        source_name="Ichimoku Kinko Hyo (Hosoda) + MACD (Appel)",
        source_url="https://www.investopedia.com/terms/i/ichimoku-cloud.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
