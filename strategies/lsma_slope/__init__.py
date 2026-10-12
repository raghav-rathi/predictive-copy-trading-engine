"""LSMA slope engine: registration + re-exports."""

from strategies.lsma_slope import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="LSMA Slope (Least Squares Moving Average)",
        slug="lsma_slope",
        description=(
            "Least-squares regression endpoint LSMA(21): long when close > "
            "LSMA and 5-bar LSMA slope > 0, short mirrored, exit on slope "
            "flip."
        ),
        source_name="Least Squares Moving Average — standard TA definition",
        source_url="https://www.updata.co.uk/technical-analysis-glossary",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
