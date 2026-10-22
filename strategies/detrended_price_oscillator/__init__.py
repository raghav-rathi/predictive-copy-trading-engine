"""DPO zero-line cross engine: registration + re-exports."""

from strategies.detrended_price_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DPO Zero-Line Cross",
        slug="detrended_price_oscillator",
        description=(
            "Detrended Price Oscillator: dpo = close - "
            "SMA(close, 20).shift(11); long on a zero-line cross-up "
            "only while close > SMA(50), short on a zero-line cross-down "
            "only while close < SMA(50); exits on the opposite zero-cross "
            "regardless of trend; 2xATR stop, 2.5xATR chandelier trail, "
            "150-bar max hold."
        ),
        source_name="Detrended Price Oscillator (Ehlers/Investopedia convention)",
        source_url="https://capital.com/en-eu/learn/technical-analysis/detrended-price-oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
