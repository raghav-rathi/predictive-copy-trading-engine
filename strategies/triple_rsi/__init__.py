"""Triple RSI: registration + re-exports."""

from strategies.triple_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Triple RSI",
        slug="triple_rsi",
        description="RSI(7), RSI(14) and RSI(21) (Wilder): long when all three are above 55, triggered on the bar the last crosses above 55; short when all three are below 45, triggered on the bar the last crosses below 45. Exit a long when any RSI crosses below 50, a short when any crosses above 50, plus the harness stop/trail.",
        source_name="Triple RSI momentum confirmation (RSI 7/14/21, 55/45 thresholds; RSI definition per Investopedia)",
        source_url="https://www.investopedia.com/terms/r/rsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
