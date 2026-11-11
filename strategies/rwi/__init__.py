"""Random Walk Index: Chande & Kroll trend-strength entry (registration + re-exports)."""

from strategies.rwi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Random Walk Index",
        slug="rwi",
        description="Chande & Kroll Random Walk Index (n=14): long when RWI-high crosses above 1.0, short when RWI-low crosses above 1.0; exit on the opposite RWI crossing above 1.0. A reading above 1.0 means price moved further in 14 bars than a random walk would typically travel in one bar.",
        source_name="Chande & Kroll — The New Technical Trader (1994)",
        source_url="https://www.investopedia.com/terms/r/random-walk-index.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
