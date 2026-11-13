"""MACD signal-line crossover: registration + re-exports."""

from strategies.macd_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Signal-Line Crossover",
        slug="macd_cross",
        description="Gerald Appel's MACD(12,26,9): long on the MACD line crossing above its 9-period signal line, short on crossing below, exit on the opposite cross, with the harness stop/trail as the exit mechanism.",
        source_name="Gerald Appel — MACD (1979)",
        source_url="https://www.investopedia.com/terms/m/macd.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
