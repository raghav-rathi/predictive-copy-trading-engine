"""Bill Williams' Alligator + fractal engine: registration + re-exports."""

from strategies.williams_alligator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Williams Alligator + Fractal",
        slug="williams_alligator",
        description=(
            "Bill Williams' Alligator (SMMA 13/8/5 of median, shifted 8/5/3) "
            "with fractal breakout entries: long when a confirmed buy-fractal "
            "high breaks above the teeth with lips > teeth > jaw, mirror for "
            "shorts; exit on opposite break or lips/teeth sleep cross; "
            "1.5xATR stop (fractal-extreme approx), 72-bar max hold."
        ),
        source_name="Bill Williams — Profitunity / Alligator + Fractal (Trading Chaos)",
        source_url="https://forexstrategiesresources.com/metatrader-trading-system-ii/239-profitunity-chaos-trading-system-by-bill-williams/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
