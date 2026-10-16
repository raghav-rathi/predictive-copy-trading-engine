"""Episodic-pivot engine: registration + re-exports."""

from strategies.episodic_thrust import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Episodic pivots (crypto adaptation)",
        slug="episodic_thrust",
        description=(
            "Neglect base (tight 30-bar coil, dry volume) broken by a "
            "2xATR / 2x-volume thrust closing near its high; long only; "
            "first-down-bar exit, 2xATR stop, 3xATR trail, 30-bar hold."
        ),
        source_name="Pradeep Bonde Episodic Pivots (stockbee; crypto adaptation)",
        source_url="https://www.tradezella.com/strategies/episode-pivot-strategy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
