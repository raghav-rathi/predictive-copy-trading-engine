"""Livermore Pivotal Point: registration + re-exports."""

from strategies.livermore_pivotal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Livermore Pivotal Point",
        slug="livermore_pivotal",
        description="Jesse Livermore pivotal-point / Market Key system: a 20-bar consolidation (range < 0.6x the median 20-bar range of the prior 100 bars) freezes a bull/bear pivot; a close through the pivot on volume > 1.25x the 20-bar mean is the break, a pullback that holds the pivot on contracting volume within 10 bars is the natural reaction, and a close beyond the reaction extreme on expanding volume is the entry; exit on the opposite signal or a close back through the pivot (the danger signal), plus the harness stop/trail.",
        source_name="Livermore pivotal point (MQL5; How to Trade in Stocks, 1940)",
        source_url="https://www.mql5.com/en/articles/24075",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
