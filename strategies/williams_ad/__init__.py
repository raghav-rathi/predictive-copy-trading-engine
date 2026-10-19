"""Williams A/D engine: registration + re-exports."""

from strategies.williams_ad import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Williams Accumulation/Distribution",
        slug="williams_ad",
        description=(
            "Larry Williams A/D cumulative pressure series; 20-bar SMA of "
            "WAD and 50-bar SMA of price; long when price is above its "
            "SMA50 and WAD crosses above its SMA20, short mirrors; exit on "
            "the cross back; 2xATR stop, 60-bar max hold."
        ),
        source_name="cTrader Help — Williams Accumulation/Distribution",
        source_url="https://help.ctrader.com/indicators/built-in/other/williams-accumulation-distribution/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
