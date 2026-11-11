"""Ehlers RSI: Wilder RSI on SuperSmoother-filtered closes (registration + re-exports)."""

from strategies.ehlers_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ehlers RSI",
        slug="ehlers_rsi",
        description="John Ehlers' RSI on SuperSmoother(10)-filtered closes (Cycle Analytics for Traders, 2013): Wilder RSI(14) computed on the smoothed series. Long on RSI crossing above 30, short on RSI crossing below 70; long exit on RSI crossing above 70, short exit on RSI crossing below 30. Distinct from adaptive_rsi (Kaufman-AMA based).",
        source_name="John F. Ehlers — Cycle Analytics for Traders (2013)",
        source_url="https://www.investopedia.com/terms/r/rsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
