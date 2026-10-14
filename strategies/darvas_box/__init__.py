"""Darvas Box engine: registration + re-exports."""

from strategies.darvas_box import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Darvas Box (box-top breakout, long-only)",
        slug="darvas_box",
        description=(
            "Box top = 60-bar high unbroken for 3 bars; buy the "
            "volume-confirmed close above the top, exit below the box floor."
        ),
        source_name="Darvas Box (Nicolas Darvas) — MQL5 Part 7",
        source_url="https://www.mql5.com/en/articles/24111",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
