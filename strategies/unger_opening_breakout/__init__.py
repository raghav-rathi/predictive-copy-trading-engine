"""Unger opening-breakout engine: registration + re-exports."""

from strategies.unger_opening_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Unger Opening Breakout",
        slug="unger_opening_breakout",
        description=(
            "Andrea Unger's championship intraday breakout: the first 3 "
            "hourly bars of the UTC day set the range; enter on the first "
            "close beyond it, one trade per side per day, no take profit "
            "(1.5xATR chandelier trail), 1.5xATR stop, flat by session end."
        ),
        source_name="Andrea Unger interview (4x World Cup Trading Champion)",
        source_url="https://bettersystemtrader.com/016-andrea-unger/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
