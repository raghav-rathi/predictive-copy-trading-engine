"""Rob Carver EWMAC forecast engine: registration + re-exports."""

from strategies.carver_ewmac import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EWMAC Forecast (Rob Carver)",
        slug="carver_ewmac",
        description=(
            "EWMAC(8,32)+(16,64)+(32,128) of close, each z-scored by its "
            "252-bar rolling std and averaged; forecast = clip(10*z, +-20); "
            "long on cross above +10, short on cross below -10, flat between; "
            "2xATR stop, 120-bar max hold."
        ),
        source_name="Rob Carver, Systematic Trading + qoppac.blogspot.com EWMAC rules",
        source_url="https://qoppac.blogspot.com/2023/01/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
