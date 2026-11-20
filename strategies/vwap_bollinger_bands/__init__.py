"""VWAP Bollinger Bands: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.vwap_bollinger_bands import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="VWAP Bollinger Bands",
        slug="vwap_bollinger_bands",
        description="Session-anchored (UTC day) VWAP +/- 2.0 volume-weighted SD bands; long on a close below the lower band and short on a close above the upper band, only while ADX(14) < 25 (ranging regime); exit on a close back at/through VWAP, plus the harness stop/trail.",
        source_name="VWAP mean-reversion strategy (Tarrow Futures)",
        source_url="https://www.tarrowfutures.com/blog/vwap-mean-reversion-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
