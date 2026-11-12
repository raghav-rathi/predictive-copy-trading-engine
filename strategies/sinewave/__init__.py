"""SineWave: registration + re-exports."""

from strategies.sinewave import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SineWave",
        slug="sinewave",
        description="John F. Ehlers' SineWave (Cybernetic Analysis for Stocks and Futures, 2004): Hilbert transform of detrended median price gives the instantaneous cycle phase; SineWave = sin(phase), LeadSine = sin(phase + 45 deg). Long when SineWave crosses above LeadSine, short on the cross below; exit on the opposite cross, with the harness stop/trail as the exit mechanism.",
        source_name="John F. Ehlers — SineWave indicator, Cybernetic Analysis for Stocks and Futures (2004)",
        source_url="https://ta-lib.org/functions/ht_sine.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
