"""Turn-of-the-month calendar effect: registration + re-exports."""

from strategies.turn_of_month import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Turn of the Month",
        slug="turn_of_month",
        description="Long-only calendar effect (Lakonishok & Smidt window): long on the first bar of the last calendar day of each month (00:00 UTC bar, fills next open) and exit on the 23:00 UTC bar of the 3rd calendar day of the next month; no shorts; date logic from the bar timestamp in UTC only, plus the harness stop/trail/max-hold.",
        source_name="Turn of the month in equity indexes (Quantpedia)",
        source_url="https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
