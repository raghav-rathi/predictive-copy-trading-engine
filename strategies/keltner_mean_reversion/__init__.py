"""Keltner mean-reversion engine: registration + re-exports."""

from strategies.keltner_mean_reversion import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner Mean Reversion",
        slug="keltner_mean_reversion",
        description=(
            "Keltner channel fade (Raschke): EMA(20) midline, "
            "ATR(10) bands at 2.0x. Long on a close crossing "
            "below the lower band on a bullish candle; short "
            "on a close crossing above the upper band on a "
            "bearish candle. Exit on a cross back to the "
            "midline or the opposite entry; 2xATR stop, 3xATR "
            "trail, 72-bar max hold."
        ),
        source_name="Keltner channel strategy (Loomi AI)",
        source_url="https://www.loomiai.io/learn/keltner-channel-strategy-backtest/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
