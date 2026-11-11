"""Early Onset Trend: Ehlers' quotient-transform trend detector (registration + re-exports)."""

from strategies.ehlers_early_onset_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Early Onset Trend",
        slug="ehlers_early_onset_trend",
        description="John Ehlers' Early Onset Trend (TASC Aug 2014, 'The Quotient Transform'): a 100-bar roofing filter feeds a SuperSmoother(30), normalised by a fast-attack/slow-decay peak tracker and passed through the quotient transform with K1=0.85 and K2=0.40. Long on Quotient1 crossing above 0, short on Quotient2 crossing below 0; exit on the opposite quotient's zero cross.",
        source_name="John F. Ehlers — The Quotient Transform (TASC Aug 2014)",
        source_url="http://traders.com/documentation/feedbk_docs/2014/08/TradersTips.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
