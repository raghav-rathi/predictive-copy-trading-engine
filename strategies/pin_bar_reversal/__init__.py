"""Pin bar reversal: registration + re-exports."""

from strategies.pin_bar_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pin Bar Reversal",
        slug="pin_bar_reversal",
        description=(
            "Pin bar / Pinocchio bar rejection (Martin Pring price-action "
            "canon): enter long on a bullish pin — lower wick >= 2/3 of the "
            "bar range, body <= 1/3, upper wick <= 0.2, at a 5-bar swing "
            "low — and short on the mirror image at a 5-bar swing high; "
            "exit on the opposite rejection; 1xATR stop beyond the tail, "
            "2R (2xATR) target, 48-bar max hold, both sides."
        ),
        source_name="Pin bar reversal (Pring price-action canon)",
        source_url=(
            "https://halleytech.substack.com/p/reversal-candlestick-patterns"
        ),
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
