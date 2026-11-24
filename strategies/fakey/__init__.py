"""Fakey (false break of an inside bar) engine: registration + re-exports."""

from strategies.fakey import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fakey",
        slug="fakey",
        description=(
            "Nial Fuller Fakey: an inside bar (i-1) inside a mother bar "
            "(i-2), then bar i breaks the inside bar's extreme but "
            "closes back inside the mother bar's range — long on a "
            "false downside break, short on a false upside break; "
            "exit on the opposite signal; 2xATR stop, 3xATR "
            "chandelier trail, 60-bar max hold."
        ),
        source_name="Nial Fuller, Fakey pattern",
        source_url="https://www.learntotradethemarket.com/forex-trading-strategies/what-is-fakey-pattern",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
