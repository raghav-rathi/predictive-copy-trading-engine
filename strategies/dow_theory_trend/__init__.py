"""Dow Theory primary-trend engine: registration + re-exports."""

from strategies.dow_theory_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dow Theory Trend",
        slug="dow_theory_trend",
        description=(
            "Dow Theory primary trend on 5-bar pivots: HH+HL confirms an "
            "uptrend (LH+LL a downtrend); enter on a close above the last "
            "swing high after a 33-66% pullback, with breakout volume "
            "above its 20-bar mean; exit when swing structure breaks "
            "(lower low / higher high) or retracement exceeds 66%; "
            "2xATR stop (approx. the last swing extreme), 4xATR target "
            "(2R), 120-bar max hold."
        ),
        source_name="Dow Theory",
        source_url="https://finabase.io/learn/technical-analysis/dow-theory",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
