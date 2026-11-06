"""Wilder Volatility Stop: registration + re-exports."""

from strategies.wilder_volatility_stop import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder Volatility Stop",
        slug="wilder_volatility_stop",
        description="Welles Wilder's Volatility Stop (New Concepts in Technical Trading Systems, 1978): ATR(7) trailing stop 3xATR behind the significant close (SIC); a close through the stop flips the trend and enters the other side.",
        source_name="Welles Wilder, New Concepts in Technical Trading Systems (1978)",
        source_url="https://www.incrediblecharts.com/indicators/volatility_stops.php",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
