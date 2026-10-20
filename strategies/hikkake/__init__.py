"""Hikkake False-Breakout: registration + re-exports."""

from strategies.hikkake import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hikkake False-Breakout",
        slug="hikkake",
        description=(
            "Daniel Chesler's hikkake: an inside bar followed by a bar that "
            "prints a lower low AND lower high (failed breakdown) or higher "
            "high AND higher low (failed breakout); enter on a close back "
            "through the inside bar's range within 3 bars (the trapped "
            "side covering). 1.5xATR stop, 3.0xATR target, 20-bar max hold."
        ),
        source_name="Hikkake pattern (Chesler 2004, via forexracer.com)",
        source_url="https://www.forexracer.com/hikkake-pattern-indicator-mt5/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
