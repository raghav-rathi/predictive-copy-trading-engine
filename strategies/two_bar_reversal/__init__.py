"""2-bar key reversal engine: registration + re-exports."""

from strategies.two_bar_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Two-Bar Key Reversal",
        slug="two_bar_reversal",
        description=(
            "Larry Williams 2-bar key reversal: long when a down bar "
            "makes a lower low and the next bar closes above that "
            "bar's high; short mirror; exits on the opposite "
            "reversal; 2xATR stop, 3xATR chandelier trail, 60-bar "
            "max hold."
        ),
        source_name='Larry Williams, "Long-Term Secrets to Short-Term Trading"',
        source_url="http://www.solerinvestments.com/Online-Trading/Larry-Williams-Trading.htm",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
