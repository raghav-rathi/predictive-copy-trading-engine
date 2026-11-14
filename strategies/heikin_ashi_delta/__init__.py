"""Heikin Ashi delta momentum engine: registration + re-exports."""

from strategies.heikin_ashi_delta import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Heikin Ashi Delta Momentum",
        slug="heikin_ashi_delta",
        description=(
            "Heikin Ashi delta momentum: HA_close=(o+h+l+c)/4, "
            "HA_open=(prev HA_open+prev HA_close)/2, delta=HA_close-HA_open; "
            "long when delta crosses from negative to positive (or turns "
            "positive after >=3 negative bars) with HA_close>HA_open, short "
            "on the mirror image; exit when delta crosses back through "
            "zero; 2xATR stop, 3xATR chandelier trail, 150-bar max hold."
        ),
        source_name="Heikin Ashi trading strategy",
        source_url="https://www.babypips.com/learn/forex/how-to-trade-heikin-ashi?locale=ja",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
