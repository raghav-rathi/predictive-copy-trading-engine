"""London session breakout: registration + re-exports."""

from strategies.london_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="London Session Breakout",
        slug="london_breakout",
        description="London session breakout (PatternsWizard exact-rules version, adapted to fixed UTC hours): range = highest high / lowest low of 00:00-08:00 UTC hourly bars; entry = first 08:00-12:00 UTC bar whose close breaks the range; exit on the opposite-side break or the 16:00 UTC bar, plus the harness stop/trail.",
        source_name="London breakout strategy (PatternsWizard)",
        source_url="https://patternswizard.com/london-breakout-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
