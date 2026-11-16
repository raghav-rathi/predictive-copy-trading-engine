"""Jurik RSX engine: registration + re-exports."""

from strategies.jurik_rsx import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Jurik RSX",
        slug="jurik_rsx",
        description=(
            "Jurik RSX (public reconstruction): RSI-style ratio of "
            "signed vs absolute price change, each run through "
            "Jurik's three-stage smoothing cascade (length 14). Long "
            "on a cross above 50 with RSX rising; short mirrored. "
            "Exit on a cross back through 50 or RSX hitting 80/20; "
            "skip flat RSX (|ΔRSX| < 0.5 for 3 bars). 1.5xATR stop, "
            "2xATR target, 72-bar max hold."
        ),
        source_name="RSX (Jurik Research; Wickra docs)",
        source_url="https://docs.wickra.org/Indicators/Indicator-Rsx",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
