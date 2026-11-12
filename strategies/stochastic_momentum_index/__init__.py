"""Stochastic Momentum Index: registration + re-exports."""

from strategies.stochastic_momentum_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic Momentum Index",
        slug="stochastic_momentum_index",
        description="William Blau's Stochastic Momentum Index (Momentum, Direction, and Divergence, 1995): SMI = 100 * double-smoothed (close - range midpoint) / (0.5 * double-smoothed range) over 13 bars, EMA(25,2) smoothing. Long on a cross up through -40, short on a cross down through +40, exit on a cross back through zero, with the harness stop/trail as the exit mechanism.",
        source_name="William Blau — Stochastic Momentum Index, Momentum, Direction, and Divergence (1995)",
        source_url="https://www.alphaexcapital.com/stocks/technical-analysis-for-stock-trading/technical-indicators-for-stocks/stochastic-momentum-index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
