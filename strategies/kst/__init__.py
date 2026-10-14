"""KST engine: registration + re-exports."""

from strategies.kst import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pring Know Sure Thing momentum system",
        slug="kst",
        description=(
            "KST = weighted sum of smoothed ROC(10,15,20,30); long when "
            "KST crosses above its 9-bar signal; short on the mirror; "
            "exit on the opposite cross."
        ),
        source_name="Martin Pring — Know Sure Thing (KST)",
        source_url="https://www.investopedia.com/terms/k/know-sure-thing-kst.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
