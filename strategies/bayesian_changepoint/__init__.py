"""Bayesian changepoint engine: registration + re-exports."""

from strategies.bayesian_changepoint import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bayesian Changepoint",
        slug="bayesian_changepoint",
        description=(
            "Adams & MacKay Bayesian online changepoint detection: "
            "posterior run-length over log-returns (Gaussian "
            "likelihood, constant hazard 1/100); long/short on a "
            "detected changepoint in the direction of the "
            "post-change mean return; 1.5xATR stop, 72-bar max hold."
        ),
        source_name="Bayesian Online Changepoint Detection (Adams & MacKay 2007)",
        source_url="https://arxiv.org/pdf/0710.3742",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
