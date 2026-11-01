"""RSI Bollinger Bands: registration + re-exports."""

from strategies.rsi_bollinger_bands import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI Bollinger Bands",
        slug="rsi_bollinger_bands",
        description=(
            "Bollinger Bands applied to RSI itself: RSI(14) against its own 20-bar SMA +/- 2 standard deviations. Long when RSI crosses above its lower band, short when it crosses below its upper band, exit at the RSI middle band. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Bollinger Bands on RSI (mean-reversion construction)",
        source_url="https://www.luxalgo.com/blog/mean-reversion-strategies-for-algorithmic-trading/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
