"""Dark cloud cover: registration + re-exports."""

from strategies.dark_cloud_cover import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dark Cloud Cover",
        slug="dark_cloud_cover",
        description="Dark cloud cover after an uptrend (bar 1 closes above SMA(50)): bullish bar 1 with a body of at least 0.6x its range, bar 2 gaps above bar 1's high and closes below bar 1's midpoint — enter short on bar 2's close; exit on a close above bar 2's high. Mirror with the piercing pattern for longs.",
        source_name="Changelly — Reversal Candlestick Patterns",
        source_url="https://changelly.com/blog/reversal-candlestick-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
