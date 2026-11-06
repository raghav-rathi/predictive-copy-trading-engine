"""Wolfe Wave: registration + re-exports."""

from strategies.wolfe_wave import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wolfe Wave",
        slug="wolfe_wave",
        description="Bill Wolfe's Wolfe Wave: a 5-pivot zigzag sequence (low1, high2, lower low3, lower high4, low5 breaking below the 1-3 trendline, with the 1-3 and 2-4 lines converging) enters long on the close back above the 1-3 trendline within 20 bars and exits at the EPA line (through points 1 and 4); bearish mirror.",
        source_name="Bill Wolfe Wolfe Wave",
        source_url="https://www.luxalgo.com/library/concept/wolfe-waves/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
