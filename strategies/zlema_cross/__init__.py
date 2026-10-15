"""ZLEMA engine: registration + re-exports."""

from strategies.zlema_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Zero-Lag EMA cross (de-lagged)",
        slug="zlema_cross",
        description=(
            "De-lagged ZLEMA(10)/ZLEMA(30) cross; entries on the cross; "
            "exits on the opposite cross; 2xATR stop, 96-bar max hold."
        ),
        source_name="Zero-Lag EMA — TA-Lib zlema feature notes",
        source_url="https://github.com/ta-lib/ta-lib/commit/053e7c229eb2f5f85593d8375a521ba665dbc9aa",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
