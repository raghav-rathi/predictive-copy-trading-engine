"""Williams %R oscillator: registration + re-exports."""

from strategies.williams_r_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Williams %R Oscillator",
        slug="williams_r_oscillator",
        description="Williams %R(14) oversold/overbought exits with an SMA(50) trend filter: long when %R crosses back above -80 after being below -80 while close is above SMA(50); short when %R crosses back below -20 after being above -20 while close is below SMA(50); exit long when %R crosses above -20, exit short when %R crosses below -80.",
        source_name="Williams %R indicator (Larry Williams, 1973)",
        source_url="https://blog.ueex.com/williams-r-indicator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
