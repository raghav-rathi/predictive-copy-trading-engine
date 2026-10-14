"""Wilder DMI engine: registration + re-exports."""

from strategies.wilder_dm import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder DMI/ADX + Parabolic SAR",
        slug="wilder_dm",
        description=(
            "Wilder (1978): +DI/-DI cross with ADX(14) > 25 and rising for "
            "entries; Parabolic SAR flips, ADX < 20, or the range rule for exits."
        ),
        source_name="J. Welles Wilder, New Concepts in Technical Trading Systems (1978)",
        source_url="https://dev.to/mt5depot/adx-trend-filter-in-an-mt5-ea-wiring-it-from-blocks-and-where-it-breaks-27af",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
