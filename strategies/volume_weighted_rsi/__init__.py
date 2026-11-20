"""Volume-Weighted RSI: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.volume_weighted_rsi import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="Volume-Weighted RSI",
        slug="volume_weighted_rsi",
        description="Wilder RSI(14) computed on a rolling volume-weighted typical price VWTP(14) = sum(tp*v)/sum(v), tp=(h+l+c)/3; long when VW-RSI crosses below 30, short when it crosses above 70, exit when it crosses back through 50, plus the harness stop/trail.",
        source_name="Wilder RSI (Investopedia)",
        source_url="https://www.investopedia.com/terms/r/rsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
