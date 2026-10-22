"""Chaikin Volatility Expansion engine: registration + re-exports."""

from strategies.chaikin_volatility import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chaikin Volatility Expansion",
        slug="chaikin_volatility",
        description=(
            "Chaikin Volatility (Marc Chaikin): cv = 100 * ROC of the "
            "EMA(10) of the high-low range. Long when cv crosses above "
            "+5.0 with close above SMA50, short when cv crosses above "
            "+5.0 with close below SMA50 (trade WITH the trend into "
            "volatility expansion); exit when cv crosses back below the "
            "trigger or below zero; 2xATR stop, 1.5xATR chandelier "
            "trail, 100-bar max hold."
        ),
        source_name="Chaikin Volatility (Marc Chaikin)",
        source_url="https://www.spread-betting.com/trader-training/chaikin-volatility-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
