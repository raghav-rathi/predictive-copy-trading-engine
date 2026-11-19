"""Judas swing (ICT session-open fakeout reversal): registration + re-exports."""

from strategies.judas_swing import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Judas Swing",
        slug="judas_swing",
        description="ICT Judas swing: per UTC day, the Asian range is the prior evening's 20:00-00:00 UTC high/low; in the 07:00-10:00 UTC London window a wick sweeping beyond the range that closes back inside (reclaim) and then closes beyond the highest high / lowest low printed since the sweep bar is a fakeout reversal — long on the bullish shift, short on the bearish shift; entries valid only until 12:00 UTC, one signal per day per side; exit on the opposite Judas signal or a close beyond the sweep extreme, plus the harness stop/trail.",
        source_name="Judas Swing (FundingPips)",
        source_url="https://fundingpips.com/ar/blog/judas-swing-forex",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
