"""QQE engine: registration + re-exports."""

from strategies.qqe import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="QQE trailing-level cross (Glaz)",
        slug="qqe",
        description=(
            "Smoothed RSI(14) with fast/slow volatility trailing levels; "
            "entries on Fast-TL/Slow-TL cross; exits on the opposite "
            "cross; 1.5xATR stop, 72-bar max hold."
        ),
        source_name="Quantitative Qualitative Estimation — TradingPedia",
        source_url="https://www.tradingpedia.com/forex-trading-indicators/quantitative-qualitative-estimation/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
