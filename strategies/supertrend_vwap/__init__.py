"""Supertrend VWAP engine: registration + re-exports."""

from strategies.supertrend_vwap import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Supertrend VWAP",
        slug="supertrend_vwap",
        description=(
            "Supertrend(10, 3.0) + UTC-day session VWAP agreement: long when Supertrend is long and the close is above the session VWAP, short when Supertrend is short and the close is below the session VWAP; exit when Supertrend flips or the close crosses the session VWAP against the position; 2xATR stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="Supertrend indicator (Olivier Seban) + session VWAP",
        source_url="https://www.investopedia.com/supertrend-indicator-7976167",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
