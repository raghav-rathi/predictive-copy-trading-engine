"""MACD Histogram Divergence: registration + re-exports."""

from strategies.macd_histogram_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Histogram Divergence",
        slug="macd_histogram_divergence",
        description="Gerald Appel MACD(12, 26, 9) divergence on confirmed swing pivots: a confirmed swing low lower than the previous one within 60 bars while the MACD histogram at that low is higher (and turns up on the confirmation bar) is a bullish divergence long; the mirror is a bearish divergence short. Exits are the opposite divergence or a histogram zero-line cross; plus the harness stop/trail.",
        source_name="Gerald Appel, MACD (Moving Average Convergence Divergence)",
        source_url="https://en.wikipedia.org/wiki/MACD",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
