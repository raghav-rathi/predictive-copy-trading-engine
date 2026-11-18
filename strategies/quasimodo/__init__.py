"""Quasimodo / over-and-under reversal: registration + re-exports."""

from strategies.quasimodo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Quasimodo Reversal",
        slug="quasimodo",
        description="Quasimodo / over-and-under reversal on causal 5-bar pivots: bearish QM is H1, pullback low L1, higher head H2, close below L1, then a failed retracement toward H1 — short on a close below the retracement leg's swing low; bullish is the mirror; exit on the opposite QM signal or a close through the head, plus the harness stop/trail.",
        source_name="Quasimodo pattern (The Right Trader; Pivex)",
        source_url="https://therighttrader.com/learn/chart-patterns/quasimodo-pattern",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
