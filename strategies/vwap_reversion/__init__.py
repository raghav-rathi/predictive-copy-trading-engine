"""VWAP reversion engine: registration + re-exports."""

from strategies.vwap_reversion import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Anchored VWAP Reversion",
        slug="vwap_reversion",
        description=(
            "Daily-anchored VWAP z-score: fade stretches beyond 1.5 ATR, "
            "exit at VWAP; 1.5xATR stop, 24-bar max hold."
        ),
        source_name="Institutional VWAP mean-reversion (public mechanics)",
        source_url="https://www.investopedia.com/terms/v/vwap.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
