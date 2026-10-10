"""Connors RSI(2) pullback engine: registration + re-exports."""

from strategies.connors_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Connors RSI pullback (R3)",
        slug="connors_rsi",
        description=(
            "RSI(2) pullback entries inside the 200MA trend: buy RSI2<10 "
            "after 3 down-bars above SMA200, exit RSI2>70; mirror shorts."
        ),
        source_name="Connors RSI2 Classic (Larry Connors) — MQL5 writeup",
        source_url="https://www.MQL5.com/en/articles/17636",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
