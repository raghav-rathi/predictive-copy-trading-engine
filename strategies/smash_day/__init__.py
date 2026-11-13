"""Smash Day: registration + re-exports."""

from strategies.smash_day import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Smash Day",
        slug="smash_day",
        description="Larry Williams' Smash Day (Long-Term Secrets to Short-Term Trading, 1999): an inside day following a wide-range day (range > 1.5x the 20-day mean) sets up a trade on the break of the inside day's high/low, valid for the next two days. Long on a close above the inside high, short on a close below the inside low; exit on the opposite break, with the harness stop/trail as the exit mechanism.",
        source_name="Larry Williams — Smash Day, Long-Term Secrets to Short-Term Trading (1999)",
        source_url="https://www.investopedia.com/terms/i/insideday.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
