"""Raschke Tail engine: registration + re-exports."""

from strategies.raschke_tail import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name='Linda Raschke "Tail" (Street Smarts)',
        slug="raschke_tail",
        description=(
            "Long-wick bar printing a 20-bar extreme triggers a buy/sell "
            "stop above/below the tail bar; 2xATR stop, 3xATR trail, "
            "48-bar max hold."
        ),
        source_name='Linda Raschke "Tail" (Street Smarts, 1996)',
        source_url="https://lindaraschke.net/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
