"""ADX/DMI engine: registration + re-exports."""

from strategies.adx_dmi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder ADX/DMI trend system",
        slug="adx_dmi",
        description=(
            "Long when +DI crosses above -DI with ADX(14) >= 25; "
            "short on the mirror cross; exit on opposite DI cross or "
            "ADX fading below 20."
        ),
        source_name="J. Welles Wilder — Directional Movement (New Concepts in Technical Trading Systems, 1978)",
        source_url="https://www.investopedia.com/terms/a/adx.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
