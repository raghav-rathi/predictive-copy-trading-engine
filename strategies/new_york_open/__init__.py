"""New York open momentum: registration + re-exports."""

from strategies.new_york_open import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="New York Open Momentum",
        slug="new_york_open",
        description="New York open momentum (ICT Power of 3): the NY open is fixed at 13:00 UTC and the first-hour range is the 13:00 UTC bar's high/low; during 14:00-17:00 UTC a close above the range high is long, a close below the range low is short, first break of the day per side only; exit at the close of the 21:00 UTC bar or on the opposite break, plus the harness stop/trail.",
        source_name="Power of 3 (Proptary)",
        source_url="https://www.proptary.com/education/power-of-3-ict",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
