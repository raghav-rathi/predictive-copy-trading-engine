"""Supertrend + ADX Filter: registration + re-exports."""

from strategies.supertrend_adx_filter import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Supertrend + ADX Filter",
        slug="supertrend_adx_filter",
        description=(
            "Supertrend direction flips gated by ADX(14) above 25, so flips only trade when a real trend is present; exit on the opposite flip."
        ),
        source_name="Supertrend (Olivier Seban) + ADX (J. Welles Wilder)",
        source_url="https://www.investopedia.com/terms/a/adx.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
