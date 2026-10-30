"""POC migration: registration + re-exports."""

from strategies.poc_migration import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="POC Migration",
        slug="poc_migration",
        description=(
            "Rolling volume-profile Point of Control trend: POC from "
            "a 50-bar, 20-bin volume profile. Long when POC has risen "
            "vs 10 bars ago and close is above POC; short on the "
            "mirror; exit when POC direction flips. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Volume Profile / Point of Control (MarketTrace explainer)",
        source_url="https://markettrace.ai/blog/volume-profile-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
