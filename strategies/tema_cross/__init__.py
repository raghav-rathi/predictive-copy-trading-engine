"""TEMA Cross: registration + re-exports."""

from strategies.tema_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TEMA Cross",
        slug="tema_cross",
        description="Patrick Mulloy TEMA(9) vs TEMA(21) cross, no regime filter: long when TEMA(9) crosses above TEMA(21), short on the cross below, exit on the opposite cross.",
        source_name="Patrick Mulloy — Triple Exponential Moving Average (TEMA)",
        source_url="https://abovethegreenline.com/what-is-the-triple-exponential-moving-average-tema/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
