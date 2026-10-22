"""DEMA Trend Cross engine: registration + re-exports."""

from strategies.dema_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DEMA Trend Cross",
        slug="dema_trend",
        description=(
            "DEMA (Mulloy): DEMA = 2*EMA(close,n) - EMA(EMA(close,n),n), "
            "long when DEMA(21) crosses above DEMA(55), short on the "
            "cross below; exits are the opposite cross; 2xATR stop, "
            "2.5xATR chandelier trail, 200-bar max hold."
        ),
        source_name="DEMA (Patrick Mulloy, TASC Jan 1994)",
        source_url="https://forex-station.com/download/file.php?id=3525533&sid=69c919d7260e3323d4ab1f31c1bb8753",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
