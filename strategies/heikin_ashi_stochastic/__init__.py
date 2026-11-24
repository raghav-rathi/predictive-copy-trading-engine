"""Heikin Ashi + Stochastic engine: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.heikin_ashi_stochastic import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Heikin Ashi + Stochastic",
        slug="heikin_ashi_stochastic",
        description=(
            "Heikin Ashi trend filter (ha_close > ha_open and above "
            "the EMA(50) of ha_close) plus a Stochastic(14,3) %K/%D "
            "cross out of oversold/overbought: LONG on a %K cross "
            "above %D while %K < 30, SHORT on a %K cross below %D "
            "while %K > 70; exit on the opposite cross. 2xATR stop, "
            "3xATR trail, 60-bar max hold."
        ),
        source_name="Heikin Ashi (Munehisa Homma) + Stochastic Oscillator (George Lane)",
        source_url="https://school.stockcharts.com/doku.php?id=chart_analysis:heikin_ashi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
