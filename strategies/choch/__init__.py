"""Change of Character (ChoCh): registration + re-exports."""

from strategies.choch import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Change of Character",
        slug="choch",
        description="Change of Character: short when an uptrend's protected higher low breaks on a displacement candle (body > 1.5x ATR), long on the mirror break of a downtrend's protected lower high; exit on the opposite ChoCh or when the close exceeds the last swing extreme, plus the harness stop/trail.",
        source_name="GoForexHub BOS and ChoCh guide; ICTradingConcepts ChoCh",
        source_url="https://www.goforexhub.com/en/guides/trading-course-ict-smc-algo/bos-and-choch",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
