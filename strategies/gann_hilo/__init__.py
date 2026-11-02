"""Gann HiLo Activator: registration + re-exports."""

from strategies.gann_hilo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gann HiLo Activator",
        slug="gann_hilo",
        description=(
            "Krausz Gann Hi-Lo Activator (SMA(3) of highs/lows, state flips on close beyond the previous opposite SMA); long on flip to bullish, short on flip to bearish."
        ),
        source_name="Gann Hi-Lo Activator (Robert Krausz, Stocks & Commodities 1998)",
        source_url="https://financial-hacker.com/petra-on-programming-the-gann-hi-lo-activator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
