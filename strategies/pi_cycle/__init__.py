"""Pi Cycle Top engine: registration + re-exports."""

from strategies.pi_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pi Cycle Top",
        slug="pi_cycle",
        description=(
            "Philip Swift's Pi Cycle Top regime system: long while "
            "SMA(111) sits below 2.0xSMA(350), short in the top zone "
            "where SMA(111) >= 2.0xSMA(350); entries on the crosses "
            "in and out of the zone, exits on the opposite cross; "
            "2xATR stop, 3xATR chandelier trail, no max hold (a "
            "regime trade, not a scalp)."
        ),
        source_name="Philip Swift, Pi Cycle Top Indicator (2019)",
        source_url="https://charts.perly.io/chart/pi-cycle",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
