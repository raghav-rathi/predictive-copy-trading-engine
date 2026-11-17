"""CCI + MACD combo: registration + re-exports."""

from strategies.cci_macd_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="CCI + MACD Combo",
        slug="cci_macd_combo",
        description="CCI(14) + MACD(12, 26, 9): long when CCI crosses up through -100 while the MACD line is above its signal line, short when CCI crosses down through +100 while the MACD line is below its signal line. Exit when CCI crosses back through 0, plus the harness stop/trail.",
        source_name="CCI + MACD strategy (The Forex Geek; UMA Technology)",
        source_url="https://theforexgeek.com/cci-macd-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
