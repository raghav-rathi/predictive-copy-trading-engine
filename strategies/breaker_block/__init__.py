"""Breaker Block: registration + re-exports."""

from strategies.breaker_block import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Breaker Block",
        slug="breaker_block",
        description="ICT Smart Money Concepts breaker block (Michael J. Huddleston). An order block is the last down-closed bar before an impulsive close above the 20-bar high (bullish) or the last up-closed bar before a close below the 20-bar low (bearish). When price returns to the block and closes through it, the block fails and flips polarity: a failed bullish OB becomes a bearish breaker — short on the retest (first bar closing back below the zone after a bar closed back into it); a failed bearish OB becomes a bullish breaker — long on the retest. Only the most recent unmitigated breaker per direction is active; a breaker expires after 200 bars or once traded. Exits on the opposite breaker signal, with the harness stop/trail as the exit mechanism.",
        source_name="ICT Smart Money Concepts — Breaker Block (Michael J. Huddleston)",
        source_url="https://www.fundedenigma.com/education/ict-concepts-decoded/power-of-three",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
