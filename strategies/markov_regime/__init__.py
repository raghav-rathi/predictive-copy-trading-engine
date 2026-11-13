"""Markov Regime Switching: registration + re-exports."""

from strategies.markov_regime import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Markov Regime Switching",
        slug="markov_regime",
        description="Hamilton (1989) Markov regime-switching: a 2-state Gaussian HMM on 1h log returns, implemented from scratch with numpy (forward-backward EM, 25 iterations). The HMM is fit once on the first 1000 bars per coin, then the causal forward filter classifies each bar as calm (low-vol) or turbulent (high-vol). Calm: EMA(12)/EMA(26) cross trend system. Turbulent: RSI(14) mean reversion (long on cross up through 30, short on cross down through 70, exit at 50).",
        source_name="James D. Hamilton — A New Approach to the Economic Analysis of Nonstationary Time Series (1989)",
        source_url="https://doi.org/10.2307/1912559",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
