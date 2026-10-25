"""Classic pivot breakout: registration + re-exports."""

from strategies.classic_pivots import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Classic Pivot Breakout",
        slug="classic_pivots",
        description=(
            "Floor-trader pivots from the prior bar: long on a close above "
            "R1 = 2*PP - L, short on a close below S1 = 2*PP - H, exit on a "
            "close back through PP = (H+L+C)/3. 1.5xATR stop, 2xATR trail, "
            "72-bar max hold."
        ),
        source_name="Classic floor-trader pivot formula (PP/R1/S1 from prior-period HLC)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
