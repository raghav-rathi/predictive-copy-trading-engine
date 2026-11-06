"""EMA Pullback: registration + re-exports."""

from strategies.ema_pullback import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EMA Pullback",
        slug="ema_pullback",
        description="Classic trend-following pullback continuation: trade in the direction of EMA(50) after price pulls back to touch the EMA(20) band and turns back in the trend direction.",
        source_name="EMA pullback trend continuation (classic trend-following)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
