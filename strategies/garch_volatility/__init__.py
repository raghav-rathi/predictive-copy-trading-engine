"""GARCH(1,1) volatility-regime trend system: registration + re-exports."""

from strategies.garch_volatility import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="GARCH Volatility",
        slug="garch_volatility",
        description="Bollerslev (1986) GARCH(1,1) volatility-regime trend system: forecast variance sigma2_t = omega + alpha*r_{t-1}^2 + beta*sigma2_{t-1} with fixed a priori params omega=1e-8, alpha=0.08, beta=0.90 on 1h log returns (no MLE fitting). Long on a close above the 20-bar high when forecast vol is inside its trailing-1000-bar 30th-70th percentile band; short on a close below the 20-bar low under the same vol condition. Exit when the close falls back inside the 20-bar range, plus the harness stop/trail.",
        source_name="Bollerslev (1986) GARCH(1,1) — Autoregressive Conditional Heteroskedasticity",
        source_url="https://en.wikipedia.org/wiki/Autoregressive_conditional_heteroskedasticity",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
