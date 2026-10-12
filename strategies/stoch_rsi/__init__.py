"""StochRSI engine: registration + re-exports."""

from strategies.stoch_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="StochRSI (Chande & Kroll, 1994)",
        slug="stoch_rsi",
        description=(
            "RSI(14) stochastics over 14 bars, %K(3)/%D(3): long on %K crossing "
            "above %D below 20, short on %K crossing below %D above 80, exit on "
            "opposite cross."
        ),
        source_name="StochRSI (Tushar Chande & Stanley Kroll, 1994) — Investopedia",
        source_url="https://www.investopedia.com/terms/s/stochrsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
