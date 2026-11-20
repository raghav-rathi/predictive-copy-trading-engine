"""Supertrend + MACD agreement: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.supertrend_macd import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="Supertrend + MACD Agreement",
        slug="supertrend_macd",
        description="Supertrend(10, 3.0 ATR) direction + MACD(12,26,9) histogram agreement: long on the first bar Supertrend is bullish and the histogram is positive, short on the mirror; exit on a Supertrend flip or a histogram sign flip against the position, plus the harness stop/trail.",
        source_name="Supertrend (Olivier Seban) + MACD (Gerald Appel)",
        source_url="https://www.tradingview.com/support/solutions/43000594684-supertrend/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
