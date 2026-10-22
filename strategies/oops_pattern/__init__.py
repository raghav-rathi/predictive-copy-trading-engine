"""Oops gap-reversion engine: registration + re-exports."""

from strategies.oops_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Oops Gap Reversion",
        slug="oops_pattern",
        description=(
            "Larry Williams' Oops pattern adapted to 1h crypto bars: a "
            "'day' is a 24-bar session, and a gap is a bar opening beyond "
            "the completed prior session's extreme (open < prior session "
            "low / open > prior session high). Long when the first bar "
            "within 24 bars of a gap-down closes back above the prior "
            "session's low (the 'oops' being satisfied); short on the "
            "mirror. Exits on the opposite Oops signal; 1.5xATR stop, "
            "24-bar max hold (flat by session end)."
        ),
        source_name="Oops Pattern (Larry Williams)",
        source_url="https://tr.tradingview.com/chart/AMZN/jING0osQ-The-OOPS-Pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
