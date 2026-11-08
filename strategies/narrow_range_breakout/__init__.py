"""Narrow-range breakout (NR7): registration + re-exports."""

from strategies.narrow_range_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Narrow-Range Breakout (NR7)",
        slug="narrow_range_breakout",
        description="Toby Crabel NR7: the setup bar's range is the smallest of the last 7 bars; within 24 bars after a setup, close above the setup high (uptrend at setup, SMA50 > SMA200) enters long, close below the setup low (downtrend at setup) enters short; exit on a close back through the setup bar's opposite extreme or on a new opposite-trend setup.",
        source_name="Clear Tape — NR7 and Inside Day Breakout Strategy",
        source_url="https://cleartape.ai/strategies/nr7-inside-day-breakout",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
