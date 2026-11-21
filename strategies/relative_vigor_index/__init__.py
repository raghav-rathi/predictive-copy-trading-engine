"""Relative Vigor Index: registration + re-exports."""

from strategies.relative_vigor_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Relative Vigor Index",
        slug="relative_vigor_index",
        description="John Ehlers Relative Vigor Index: RVI = [(c-o) + 2*(c1-o1) + 2*(c2-o2) + (c3-o3)] / [(h-l) + 2*(h1-l1) + 2*(h2-l2) + (h3-l3)] (zero denominator -> 0); signal = (RVI + 2*RVI1 + 2*RVI2 + RVI3)/6. Long on an RVI cross up through signal, short on a cross down; exit on the opposite cross, plus the harness stop/trail.",
        source_name="John Ehlers, 'Cybernetic Analysis for Stocks and Futures' (2004)",
        source_url="https://www.bybit.com/en/wiki/article/relative-vigor-index-rvi-vs-rsi-differences/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
