"""Wilder ADX/DMI trend system: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.adx_dmi_trend import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder ADX/DMI Trend System",
        slug="adx_dmi_trend",
        description=(
            "Wilder ADX/DMI (1978): LONG when +DI crosses above -DI "
            "while ADX(14) > 25; SHORT on the mirror cross while "
            "ADX > 25. Exit on the opposite DI cross or ADX falling "
            "below 20. The ADX > 25 gate is Wilder's own "
            "trend-strength rule; 1h crypto spends long stretches "
            "below it, so expect long flat periods."
        ),
        source_name="J. Welles Wilder, New Concepts in Technical Trading Systems (1978)",
        source_url="https://en.wikipedia.org/wiki/Average_directional_movement_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
