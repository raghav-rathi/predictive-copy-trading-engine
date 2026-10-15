"""NVI/PVI engine: registration + re-exports."""

from strategies.nvi_pvi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="NVI/PVI regime cross (Dysart/Fosback)",
        slug="nvi_pvi",
        description=(
            "NVI accumulates pct-change on down-volume bars, PVI on "
            "up-volume bars; entries on NVI crossing its 255-bar EMA with "
            "PVI agreement; 2xATR stop, 120-bar max hold."
        ),
        source_name="Negative Volume Index — MultiCharts / Ensign (Fosback)",
        source_url="https://www.multicharts.com/support/base/volume-based-gt-negative-volume/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
