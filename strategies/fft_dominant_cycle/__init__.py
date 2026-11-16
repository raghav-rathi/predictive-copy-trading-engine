"""FFT dominant-cycle engine: registration + re-exports."""

from strategies.fft_dominant_cycle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="FFT Dominant Cycle",
        slug="fft_dominant_cycle",
        description=(
            "Rolling FFT on detrended log-closes (Hann window, 128 "
            "bars); reconstruct the signal from the top-3 dominant "
            "frequencies with period 8-64 bars; trade the "
            "reconstructed-cycle slope through an SMA(50) trend "
            "filter; 1.5xATR stop, 2.5xATR target, 96-bar max hold."
        ),
        source_name="Fourier Transform Based Trading Strategy (PyQuantLab)",
        source_url="https://pyquantlab.medium.com/a-fourier-transform-based-trading-strategy-in-backtrader-5e2d5a6d8392",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
