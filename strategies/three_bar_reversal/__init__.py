"""3-bar reversal engine: registration + re-exports."""

from strategies.three_bar_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Three-Bar Reversal",
        slug="three_bar_reversal",
        description=(
            "Joe Ross 3-bar reversal: long when a down bar is "
            "followed by a bar making a lower low but closing above "
            "the down bar's close, confirmed by the next bar "
            "closing above the hook bar's high; short mirror; exits "
            "on the opposite reversal; 2xATR stop, 3xATR chandelier "
            "trail, 60-bar max hold."
        ),
        source_name='Joe Ross, "Trading by the Book" (three-bar reversal)',
        source_url="https://www.luxalgo.com/library/concept/1-2-3-reversal/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
