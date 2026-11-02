"""Gann Fan: registration + re-exports."""

from strategies.gann_fan import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gann Fan",
        slug="gann_fan",
        description=(
            "Gann fan 1x1 angles: rising fan from the 30-bar swing low at 1 ATR/bar and falling fan from the 30-bar swing high; long on cross above the rising fan, short below the falling fan."
        ),
        source_name="Gann fan angles (W.D. Gann)",
        source_url="https://www.investopedia.com/terms/g/gannfan.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
