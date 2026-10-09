"""Funding tilt engine: registration + re-exports."""

from strategies.funding_tilt import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Funding-Rate Tilt (contrarian)",
        slug="funding_tilt",
        description=(
            "7-day z-score of Hyperliquid hourly funding: fade crowded "
            "positioning (long at z<-2, short at z>+2), exit at |z|<0.5; "
            "2xATR stop/target, 72-bar cap."
        ),
        source_name="Perp funding contrarian (documented crypto mechanism)",
        source_url="https://www.hyperliquid.xyz/docs",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
