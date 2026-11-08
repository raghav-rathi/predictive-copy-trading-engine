"""Wilder DMI crossover with ADX filter: registration + re-exports."""

from strategies.adx_di_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ADX / DI Crossover",
        slug="adx_di_cross",
        description="Wilder DMI(14): enter long when +DI crosses above -DI with ADX above 25, rising, and the DI spread at least 5; mirror for shorts. Exit on the opposite DI cross or ADX falling below 20.",
        source_name="JournalPlus — ADX Trading Strategy",
        source_url="https://journalplus.co/strategies/adx-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
