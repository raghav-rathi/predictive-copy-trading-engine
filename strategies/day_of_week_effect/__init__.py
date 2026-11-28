"""Day-of-week effect engine: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.day_of_week_effect import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Day-of-Week Effect (Bitcoin)",
        slug="day_of_week_effect",
        description=(
            "Bitcoin day-of-week seasonality, fixed from the "
            "literature: LONG Mondays (enter Sunday 23:00 UTC, "
            "exit Monday 23:00 UTC) and SHORT Thursdays (enter "
            "Wednesday 23:00 UTC, exit Thursday 23:00 UTC). "
            "Each leg fires on exactly one bar per week; 2xATR "
            "stop, 3xATR trail, 30-bar max hold."
        ),
        source_name="Day-of-week effect — Decourt et al. 2017 / Caporale & Plastun 2018; FairHatch 2026",
        source_url="https://mpra.ub.uni-muenchen.de/id/eprint/91429/contents",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
