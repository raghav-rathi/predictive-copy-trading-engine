"""Cutler RSI: registration + re-exports."""

from strategies.cutler_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Cutler RSI",
        slug="cutler_rsi",
        description=(
            "Cutler's RSI (14): Wilder's RSI with simple moving averages of gains/losses instead of Wilder smoothing. Long on cross above 30 from oversold, short on cross below 70 from overbought; exits at the opposite extreme."
        ),
        source_name="Cutler's RSI",
        source_url="https://www.investopedia.com/terms/r/rsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
