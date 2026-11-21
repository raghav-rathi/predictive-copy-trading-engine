"""Stochastic RSI Crossover: registration + re-exports."""

from strategies.stoch_rsi_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic RSI Crossover",
        slug="stoch_rsi_cross",
        description="Chande & Kroll StochRSI(14, 14, 3, 3): %K is the stochastic of RSI(14) over 14 bars (zero-range window scores 50), %D is SMA(3) of %K. Long on a %K-up-through-%D cross while %K < 20, short on a %K-down-through-%D cross while %K > 80; exit on the opposite %K/%D cross; plus the harness stop/trail.",
        source_name="Tushar Chande & Stanley Kroll, The New Technical Trader (1994)",
        source_url="https://www.investopedia.com/terms/s/stochrsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
