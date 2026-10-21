"""Know Sure Thing (KST) engine: registration + re-exports."""

from strategies.kst import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Know Sure Thing",
        slug="kst",
        description=(
            "Martin Pring's Know Sure Thing: 1*SMA(ROC(10),10) + "
            "2*SMA(ROC(15),10) + 3*SMA(ROC(20),10) + 4*SMA(ROC(30),15) "
            "against a 9-bar signal line; long on a cross-up while KST "
            "is still below zero, short on a cross-down while above "
            "zero; exits on the opposite cross; 2xATR stop, 3xATR "
            "chandelier trail, 200-bar max hold."
        ),
        source_name="Know Sure Thing (Martin Pring)",
        source_url="https://www.ebc.com/forex/know-sure-thing-indicator-explained-formula-and-strategies",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
