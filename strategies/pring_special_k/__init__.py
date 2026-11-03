"""Pring Special K: registration + re-exports."""

from strategies.pring_special_k import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pring Special K",
        slug="pring_special_k",
        description=(
            "Martin Pring Special K: weighted sum of 10/15/20/30-bar ROCs (weights 1/2/3/4), smoothed with a 10-bar MA, traded against its own 10-bar signal line. Long on K cross above signal, short on cross below; exits on the opposite cross."
        ),
        source_name="Pring Special K (Martin Pring)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:special_k",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
