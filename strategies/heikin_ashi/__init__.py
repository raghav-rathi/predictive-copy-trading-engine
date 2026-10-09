"""Heikin-Ashi trend engine: registration + re-exports."""

from strategies.heikin_ashi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Heikin-Ashi Trend System (Valcu six rules)",
        slug="heikin_ashi",
        description=(
            "HA color-change entries (prev red -> current green, skipping "
            "consolidation bars); exit on opposite-color or consolidation "
            "bar; 2xATR stop, 2.5xATR trail."
        ),
        source_name="Dan Valcu, Heikin-Ashi technique (six rules)",
        source_url="https://www.mql5.com/en/articles/91",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
