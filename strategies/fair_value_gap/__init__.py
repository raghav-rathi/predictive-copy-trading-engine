"""Fair Value Gap (ICT / Smart Money Concepts): registration + re-exports."""

from strategies.fair_value_gap import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fair Value Gap Retest",
        slug="fair_value_gap",
        description=(
            "ICT Fair Value Gap: 3-candle imbalance (l[i] > h[i-2] with an "
            "impulsive middle candle, range > 1.5xATR(14)) leaves an untraded "
            "zone; long when price later dips into the gap (l < fvg_high) and "
            "closes back above it, short on the mirror; exit when the zone is "
            "mitigated (traded through the far edge) or on the opposite "
            "signal; 2.0xATR stop (wide, approximating 'beyond the far edge "
            "+ buffer'), 2.0xATR chandelier trail, 72-bar max hold, both sides."
        ),
        source_name="ICT Fair Value Gap (innercircletrader.net / Equiti guide)",
        source_url="https://innercircletrader.net/tutorials/fair-value-gap-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
