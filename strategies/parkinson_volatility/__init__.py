"""Parkinson volatility-expansion engine: registration + re-exports."""

from strategies.parkinson_volatility import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Parkinson Volatility Expansion",
        slug="parkinson_volatility",
        description=(
            "Parkinson (1980) realized volatility: per-bar "
            "variance ln(H/L)^2 / (4*ln2), averaged over 20 "
            "bars. Enter when realized vol crosses ABOVE its "
            "60-bar SMA (volatility expansion) in the direction "
            "of the EMA(20) trend -- long if close > EMA20, "
            "short if close < EMA20. Exit on vol crossing back "
            "below its SMA or the close crossing the wrong side "
            "of EMA20; 2xATR stop, 3xATR trail, 72-bar max hold. "
            "Same trade structure as garman_klass_volatility; "
            "only the estimator differs."
        ),
        source_name="Parkinson volatility estimator (1980)",
        source_url="https://kaisquant.com/posts/range-volatility-estimators/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
