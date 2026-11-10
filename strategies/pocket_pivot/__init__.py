"""Pocket pivot: volume-footprint early entry inside a base (registration + re-exports)."""

from strategies.pocket_pivot import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pocket Pivot",
        slug="pocket_pivot",
        description="Gil Morales & Chris Kacher pocket pivot: an up bar whose volume exceeds the largest down-bar volume of the previous 10 trading days, inside a constructive uptrend (close above EMA(240), EMA(240) above EMA(1200), EMA(240) rising) and not extended (close < 1.10 x EMA(240)). Long-only; exit on close below EMA(240).",
        source_name="Gil Morales & Chris Kacher — Trade Like an O'Neil Disciple (2010)",
        source_url="https://www.luxalgo.com/library/concept/pocket-pivot/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
