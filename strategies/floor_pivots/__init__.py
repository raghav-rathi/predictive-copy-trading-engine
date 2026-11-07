"""Floor-trader pivots: registration + re-exports."""

from strategies.floor_pivots import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Floor-Trader Pivots",
        slug="floor_pivots",
        description="Classic floor-trader pivot breakout: PP/R1/S1/R2/S2 recomputed each bar from the trailing 24 completed 1h bars; close above PP is long-only, below PP short-only; enter long on a close above R1 with volume above its 20-bar average, exit at R2 or on a close back below PP (mirror for shorts).",
        source_name="EBC — How to Trade Using Classic Pivot Points",
        source_url="https://www.ebc.com/forex/how-to-trade-using-classic-pivot-points",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
