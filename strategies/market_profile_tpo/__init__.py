"""TPO value-area breakout: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.market_profile_tpo import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Market Profile TPO Value-Area Breakout",
        slug="market_profile_tpo",
        description="Rolling 168-bar TPO (time-price) market profile, 24 bins: POC is the max-TPO bin, value area is the contiguous bins around POC holding 70% of TPOs. Long on a close breaking above VAH, short on a close breaking below VAL; exit on the opposite value-area break.",
        source_name="Wikipedia — Market profile (Steidlmayer, CBOT)",
        source_url="https://en.wikipedia.org/wiki/Market_profile",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
