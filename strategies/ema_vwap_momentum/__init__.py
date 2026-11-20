"""EMA cross + session VWAP momentum: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.ema_vwap_momentum import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EMA Cross + Session VWAP Momentum",
        slug="ema_vwap_momentum",
        description="EMA(9)/EMA(21) cross + session VWAP (UTC-day anchored): long on an EMA cross above while the close is above the session VWAP, short on the mirror; exit on an EMA cross against or a close back through the VWAP against the position, plus the harness stop/trail.",
        source_name="EMA crossover + VWAP (session-anchored)",
        source_url="https://www.investopedia.com/terms/v/vwap.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
