"""ADX + MACD trend: registration + re-exports."""

from strategies.adx_macd_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ADX + MACD Trend",
        slug="adx_macd_trend",
        description=(
            "Long when ADX(14) > 25, +DI > -DI, and MACD crosses above "
            "its signal line; short mirror. Exit on the opposite MACD "
            "cross or ADX falling below 20. 2xATR stop, 2.5xATR trail, "
            "168-bar max hold."
        ),
        source_name="Wilder DMI/ADX + Appel MACD",
        source_url="https://en.wikipedia.org/wiki/Average_directional_movement_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
