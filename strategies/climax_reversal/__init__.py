"""Wyckoff climax reversal: registration + re-exports."""

from strategies.climax_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Climax Reversal",
        slug="climax_reversal",
        description="Wyckoff buying/selling climax reversal (law of effort vs result): buying climax — new 20-bar high, volume > 2x the trailing 20-bar mean, close in the lower third of the bar's range — signals a short; selling climax — new 20-bar low, volume > 2x mean, close in the upper third — signals a long. Exit on the opposite climax, plus the harness stop/trail.",
        source_name="Wyckoff method — buying/selling climax, effort vs result",
        source_url="https://patternswizard.com/wyckoff-method/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
