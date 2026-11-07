"""Cyber Cycle: registration + re-exports."""

from strategies.cyber_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Cyber Cycle",
        slug="cyber_cycle",
        description="John Ehlers' Cyber Cycle (Cybernetic Analysis for Stocks and Futures, ch. 4, 2004): smoothed price (c+2c1+2c2+c3)/6 fed through a band-pass cycle filter (alpha=0.07), then an EMA-style Signal (alpha2=0.1). Long when Signal crosses above its 1-bar-delayed value; short on the cross below; exit on the reverse cross.",
        source_name="Ehlers Cyber Cycle, Cybernetic Analysis for Stocks and Futures ch. 4 (2004)",
        source_url="https://www.luxalgo.com/library/concept/cyber-cycle/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
