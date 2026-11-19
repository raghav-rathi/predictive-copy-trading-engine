"""Mitigation block: registration + re-exports."""

from strategies.mitigation_block import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Mitigation Block",
        slug="mitigation_block",
        description="ICT mitigation block: a failure swing (lower high that never trades through the prior high, then a close below the pullback low) arms the block from the candle at the pullback low; short on the first return into it, exit on a close above the block high; bullish is the mirror, plus the harness stop/trail.",
        source_name="Mitigation Block (The Right Trader)",
        source_url="https://therighttrader.com/learn/smart-money-concepts/mitigation-block",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
