"""RSI + session VWAP engine: registration + re-exports."""

from strategies.rsi_vwap import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI VWAP",
        slug="rsi_vwap",
        description=(
            "RSI(14) + session VWAP: long on RSI crossing up "
            "through 30 while the close is above the UTC-day "
            "session VWAP, short on RSI crossing down through 70 "
            "while the close is below it; exit on RSI crossing 50 "
            "against the position or the close crossing the "
            "session VWAP against the position; 2xATR stop, "
            "3xATR trail, 120-bar max hold."
        ),
        source_name="RSI + session VWAP (standard combination; session-VWAP convention per vwap_session_breakout)",
        source_url="https://en.wikipedia.org/wiki/Relative_strength_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
