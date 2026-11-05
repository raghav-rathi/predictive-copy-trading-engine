"""VWMA crossover: registration + re-exports."""

from strategies.vwma_crossover import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="VWMA Crossover",
        slug="vwma_crossover",
        description="Volume Weighted Moving Average crossover: VWMA(10) vs VWMA(50), where VWMA(n) = sum(close*volume)/sum(volume) over n bars. Long on the fast VWMA crossing above the slow VWMA; short on crossing below; exit on the opposite cross.",
        source_name="VWMA indicator explained (OneUp Trader)",
        source_url="https://blog.oneuptrader.com/analysis/what-is-vwma-indicator-explained/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
