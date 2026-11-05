"""ADX trend system: registration + re-exports."""

from strategies.adx_trend_system import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ADX Trend System",
        slug="adx_trend_system",
        description="ADX trend system (J. Welles Wilder, 'New Concepts in Technical Trading Systems', 1978): long when +DI crosses above -DI and ADX > 25; short when -DI crosses above +DI and ADX > 25; exit on the opposite DI cross or ADX falling below 20.",
        source_name="ADX indicator (Kagels Trading)",
        source_url="https://kagels-trading.com/blog/adx-indicator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
