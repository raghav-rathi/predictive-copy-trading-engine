"""Wavelet-trend engine: registration + re-exports."""

from strategies.wavelet_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wavelet Trend",
        slug="wavelet_trend",
        description=(
            "DWT (db4, level 3) on closes, approximation-only "
            "reconstruction (denoised trend); trade its 5-bar slope: "
            "long when the slope turns positive and close is above "
            "the approximation, short on the mirror; 1.5xATR stop, "
            "2.5xATR target, 72-bar max hold."
        ),
        source_name="Wavelet Decomposition (LuxAlgo)",
        source_url="https://www.luxalgo.com/library/concept/wavelet-decomposition/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
