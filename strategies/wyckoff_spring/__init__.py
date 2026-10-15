"""Wyckoff spring engine: registration + re-exports."""

from strategies.wyckoff_spring import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wyckoff spring/upthrust (Wyckoff)",
        slug="wyckoff_spring",
        description=(
            "50-bar range shakeouts: spring (failed breakdown) longs, "
            "upthrust (failed breakout) shorts, volume-confirmed; exits "
            "at the opposite range edge; 1xATR stop, 120-bar max hold."
        ),
        source_name="The Wyckoff Method — spring/upthrust schematics",
        source_url="https://www1.stjameswinery.com/libweb/wHaXKo/275036/TheRichardDWyckoffMethodOfTradingAndInvestingInStocks.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
