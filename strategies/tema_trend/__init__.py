"""TEMA trend engine: registration + re-exports."""

from strategies.tema_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TEMA Trend (Patrick Mulloy)",
        slug="tema_trend",
        description=(
            "TEMA(n)=3*EMA1-3*EMA2+EMA3; TEMA20 vs TEMA50 cross with SMA200 "
            "regime filter; long on cross up above SMA200, short on cross "
            "down below SMA200, exit on cross back; 2.5xATR stop, 3xATR "
            "trailing, 120-bar max hold."
        ),
        source_name="Patrick Mulloy TEMA (abovethegreenline / definedgesecurities)",
        source_url="https://abovethegreenline.com/what-is-the-triple-exponential-moving-average-tema/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
