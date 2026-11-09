"""Gann Square of Nine: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.gann_square_nine import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gann Square of Nine",
        slug="gann_square_nine",
        description="Gann Square of Nine 45-degree ladder from the prior close: enter long when the close crosses above the nearest level above the prior close with that level within 0.5% of the prior close; mirror for shorts. Exit on a close back below/above the entry level or on reaching the next level up/down.",
        source_name="Investopedia — Gann Indicators Explained",
        source_url="https://www.investopedia.com/articles/trading/08/gann-indicator.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
