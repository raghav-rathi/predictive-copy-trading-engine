"""Liquidity-sweep engine: registration + re-exports."""

from strategies.liquidity_sweep import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ICT liquidity-sweep (stop-hunt) reversal system",
        slug="liquidity_sweep",
        description=(
            "Wick through the 20-bar swing extreme by >0.25 ATR with a "
            "close back inside: short the buy-side sweep, long the "
            "sell-side sweep; exit on the opposite sweep or a closing "
            "break of the level."
        ),
        source_name="ICT / SMC — Liquidity Sweep reversal mechanics",
        source_url="https://liquidityscan.io/blog/liquidity-sweep-then-structure-shift-the-stop-hunt-to-reversal-sequence",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
