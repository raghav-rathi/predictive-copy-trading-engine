"""Wilder Accumulative Swing Index: registration + re-exports."""

from strategies.wilder_accumulative_swing import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder Accumulative Swing Index",
        slug="wilder_accumulative_swing",
        description=(
            "J. Welles Wilder's Accumulative Swing Index, trend-followed "
            "on itself: SI = 50 * ((C - Cy) + 0.5*(C - O) + "
            "0.25*(Cy - Oy)) / R with R = max(H - Cy, Cy - L, H - L), "
            "ASI = cumulative SI, signal = ASI crossing its EMA(10). "
            "Long above, short below, exit on the opposite cross. "
            "2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Accumulative Swing Index (ASI) — BabyPips Forexpedia",
        source_url="https://www.babypips.com/forexpedia/accumulative-swing-index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
