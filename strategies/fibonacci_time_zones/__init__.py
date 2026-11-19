"""Fibonacci Time Zones: registration + re-exports."""

from strategies.fibonacci_time_zones import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fibonacci Time Zones Pullback",
        slug="fibonacci_time_zones",
        description="Fibonacci time zones as a timing filter on pullback entries: zones fall at Fib bar counts 8, 13, 21, 34 after the most recent confirmed 10-bar swing high/low; inside a zone window (+/-1 bar) a pullback-reversal confirms direction — after a swing-low anchor in an uptrend (close > EMA(50)), a close below EMA(20) then a close back above it is a long, and the mirror after a swing-high anchor in a downtrend is a short; exit on the opposite signal or a close through the anchor extreme, plus the harness stop/trail. Time zones alone give timing, not direction — the EMA pullback confirmation supplies direction.",
        source_name="Fibonacci time zones (The Right Trader)",
        source_url="https://therighttrader.com/learn/fibonacci-and-drawing-tools/fibonacci-time-zones",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
