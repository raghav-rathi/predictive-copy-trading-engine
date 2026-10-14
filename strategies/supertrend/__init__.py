"""Supertrend engine: registration + re-exports."""

from strategies.supertrend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Supertrend (ADX-confirmed)",
        slug="supertrend",
        description=(
            "Supertrend(10, 3.0) direction flips for entries/exits, "
            "gated by ADX(14) > 20; 2.5xATR stop + 3xATR chandelier trailing."
        ),
        source_name="Olivier Seban Supertrend (public domain formula)",
        source_url="https://www.updata.co.uk/developers/docs/libmanstrat/supertrend",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
