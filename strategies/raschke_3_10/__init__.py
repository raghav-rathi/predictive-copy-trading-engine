"""Raschke 3/10 oscillator engine: registration + re-exports."""

from strategies.raschke_3_10 import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="3/10 Oscillator (Raschke)",
        slug="raschke_3_10",
        description=(
            "SMA(3)-SMA(10) of (h+l)/2 vs SMA(16) trigger; long on cross "
            "above with osc>0, short on cross below with osc<0; exit on "
            "cross back; 1.5xATR stop, 48-bar max hold."
        ),
        source_name="Linda Raschke & Larry Connors, Street Smarts (1995)",
        source_url="https://www.tradingview.com/scripts/lindaraschke/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
