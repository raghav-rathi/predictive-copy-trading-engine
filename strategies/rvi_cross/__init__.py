"""RVI Cross: registration + re-exports."""

from strategies.rvi_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RVI Cross",
        slug="rvi_cross",
        description=(
            "John Ehlers' Relative Vigor Index: the (1,2,2,1)-weighted close-minus-open over high-minus-low, smoothed over 10 bars, against its 4-bar weighted signal line. Long on the RVI cross above its signal, short below. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Relative Vigor Index (John Ehlers)",
        source_url="https://www.investopedia.com/terms/r/relative_vigor_index.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
