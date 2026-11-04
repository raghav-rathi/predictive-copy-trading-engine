"""Elliott Wave Oscillator: registration + re-exports."""

from strategies.elliott_wave_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elliott Wave Oscillator",
        slug="elliott_wave_oscillator",
        description="Bill Williams Elliott Wave Oscillator: SMA(5) minus SMA(35) of closes. Long on a zero-line cross up confirmed by a rising SMA(50); short on a zero-line cross down confirmed by a falling SMA(50); exit on the opposite zero cross.",
        source_name="Elliott Wave Oscillator (Bill Williams)",
        source_url="https://www.daytrading.com/elliott-wave-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
