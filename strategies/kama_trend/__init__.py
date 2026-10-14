"""KAMA trend engine: registration + re-exports."""

from strategies.kama_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="KAMA trend (Kaufman adaptive MA)",
        slug="kama_trend",
        description=(
            "Price vs Kaufman AMA(10,2,30) with ER>0.3 efficiency filter; "
            "cross entries, cross-back exits."
        ),
        source_name="KAMA (Perry Kaufman) — MetaTrader 5 docs",
        source_url="https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/ama",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
