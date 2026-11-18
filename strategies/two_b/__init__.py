"""Sperandeo 2B reversal: registration + re-exports."""

from strategies.two_b import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Sperandeo 2B Reversal",
        slug="two_b",
        description="Sperandeo 2B failed retest of a 20-bar extreme: short when a new 20-bar high is retested by a close above it and a later bar closes below the retest bar's low (long is the mirror); exit on the opposite 2B signal or a close back through the arming extreme, plus the harness stop/trail.",
        source_name="Sperandeo 2B reversal (RoboForex; ThePatternSite)",
        source_url="https://roboforex.com/blog/education/trading-like-sperandeo-1-2-3-reversal-and-2b-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
