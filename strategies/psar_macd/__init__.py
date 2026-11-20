"""Parabolic SAR + MACD agreement: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.psar_macd import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Parabolic SAR + MACD Agreement",
        slug="psar_macd",
        description="Parabolic SAR (Wilder, step 0.02, max AF 0.20) flip + MACD(12,26,9) line-vs-signal agreement: long on a PSAR flip below price with the MACD line above signal, short on the mirror; exit on the opposite PSAR flip or a MACD cross against, plus the harness stop/trail.",
        source_name="Parabolic SAR (J. Welles Wilder) + MACD (Gerald Appel)",
        source_url="https://www.investopedia.com/terms/p/parabolicindicator.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
