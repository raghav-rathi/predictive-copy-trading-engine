"""Fisher Transform reversal engine: registration + re-exports."""

from strategies.fisher_transform import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fisher Transform Reversal",
        slug="fisher_transform",
        description=(
            "Ehlers Fisher Transform: normalized 10-bar price position "
            "recursively smoothed and Fisher-transformed; trigger = 1-bar lag. "
            "Long on cross above trigger, short on cross below; cross-back + "
            "extreme-level (fisher>2.5 / <-2.5) exits. Variant: ADX(14)>20 gate "
            "on entries (calibration picks winner). 2xATR stop."
        ),
        source_name="John Ehlers, Fisher Transform (Stocks & Commodities)",
        source_url="https://fxprosystems.com/ehlers-fisher-transform/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
