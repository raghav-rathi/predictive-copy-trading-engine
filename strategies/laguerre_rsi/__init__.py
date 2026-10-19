"""Laguerre RSI (John Ehlers) engine: registration + re-exports."""

from strategies.laguerre_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Laguerre RSI (John Ehlers)",
        slug="laguerre_rsi",
        description=(
            "Ehlers Laguerre RSI with gamma=0.5 (L0..L3 Laguerre-filter "
            "recurrences, CU mean, LRSI = cumup/(cumup+cumdn) in [0,1]); "
            "long on cross up through 0.2, short on cross down through 0.8, "
            "exits at the 0.5 centerline; 2xATR stop, 50-bar max hold."
        ),
        source_name="StockSharp docs, Laguerre RSI (Ehlers)",
        source_url="https://doc.stocksharp.com/en/topics/api/indicators/list_of_indicators/laguerre_rsi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
