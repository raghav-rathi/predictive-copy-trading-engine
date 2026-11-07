"""RSI(2) System: registration + re-exports."""

from strategies.rsi2_system import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI(2) System",
        slug="rsi2_system",
        description="Larry Connors' RSI(2) mean reversion (Short Term Trading Strategies That Work, 2008): trend filter SMA(200) on 1h closes; long when close > SMA(200) and RSI(2) <= 5; short when close < SMA(200) and RSI(2) >= 95; exit long when close > SMA(5), exit short when close < SMA(5).",
        source_name="Larry Connors RSI(2), Short Term Trading Strategies That Work (2008)",
        source_url="https://cleartape.ai/strategies/rsi-2-strategy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
