"""Wyckoff upthrust: registration + re-exports."""

from strategies.wyckoff_upthrust import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wyckoff Upthrust",
        slug="wyckoff_upthrust",
        description=(
            "Short-only failed-breakout trade: when price breaks above "
            "the prior-20-bar trading-range high but closes back "
            "inside the range (an upthrust / bull trap), short at the "
            "next open. Exit when price closes back above the range "
            "high (thesis invalidated). 2xATR stop, 2.5xATR trail, "
            "120-bar max hold."
        ),
        source_name="Wyckoff Method Trading — upthrust definition (TradingSim)",
        source_url="https://www.tradingsim.com/blog/wyckoff-method-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
