"""Time-series momentum engine: registration + re-exports."""

from strategies.ts_momentum import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Time-Series Momentum (Liu-Tsyvinski)",
        slug="ts_momentum",
        description=(
            "Crypto time-series momentum: volatility-scaled 1-week (168-bar) "
            "and 4-week (672-bar) past returns; long when both cross above "
            "+0.5, short when both cross below -0.5; hysteresis exits at "
            "+/-0.3; 3xATR stop, 672-bar max hold."
        ),
        source_name="Liu & Tsyvinski 2021; Liu, Tsyvinski & Wu 2022 (crypto time-series momentum)",
        source_url="https://github.com/bigcan/sharpen",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
