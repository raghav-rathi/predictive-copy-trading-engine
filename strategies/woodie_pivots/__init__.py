"""Woodie pivots: registration + re-exports."""

from strategies.woodie_pivots import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Woodie Pivots",
        slug="woodie_pivots",
        description=(
            "Woodie daily pivot breakout on 1h bars: levels from the "
            "prior completed UTC day only, PP = (H + L + 2*C) / 4, "
            "R1 = 2*PP - L, S1 = 2*PP - H. Long on a close crossing "
            "above R1, short below S1, exit back across PP. 2xATR "
            "stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Woodie pivot points",
        source_url="https://www.dumblittleman.com/pivot-points/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
