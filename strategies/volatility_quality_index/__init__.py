"""VQI engine: registration + re-exports."""

from strategies.volatility_quality_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volatility Quality Index",
        slug="volatility_quality_index",
        description=(
            "Stridsman VQI: per-bar efficiency (close change / true "
            "range), summed over 10 bars, WMA(14); long when VQI "
            "rises vs 10 bars ago, short when it falls, gated on "
            "|10-bar change| >= 0.5x its 50-bar median; 1.5xATR "
            "stop, 2R target, 48-bar max hold."
        ),
        source_name="Alpha Volatility Quality (Stridsman VQI, Coder Wolves)",
        source_url="https://in.tradingview.com/script/asS85p1B-Alpha-Trading-Alpha-Volatility-Quality-Coder-Wolves/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
