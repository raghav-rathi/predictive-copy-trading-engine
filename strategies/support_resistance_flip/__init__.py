"""Break-and-retest / role-reversal: registration + re-exports."""

from strategies.support_resistance_flip import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Support Resistance Flip",
        slug="support_resistance_flip",
        description="Break-and-retest / role-reversal: 5-bar pivot swing highs/lows over a trailing 50-bar window; a level counts only if price touched it (low within 0.5x ATR(14)) at least twice. Long on a retest-hold bar after a resistance break (low within 0.5x ATR of the level, close back above it) within 20 bars of the break; mirror for broken support. Exit on a close back across the flipped level, plus the harness stop/trail.",
        source_name="Break-and-retest strategy (Prometheus Markets; HowToTrade)",
        source_url="https://www.prometheus-markets.com/analysis-education/break-and-retest-strategy-trading-breakouts-with-confirmation/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
