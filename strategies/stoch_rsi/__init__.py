"""Stochastic RSI engine: registration + re-exports."""

from strategies.stoch_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Stochastic RSI",
        slug="stoch_rsi",
        description=(
            "Chande & Kroll Stochastic RSI: %K = SMA(3) of 100*(RSI(14) "
            "- min(RSI,14))/(max(RSI,14) - min(RSI,14)); long when %K "
            "crosses above 20 (leaves oversold), short when %K crosses "
            "below 80 (leaves overbought), exits on the 50-midline "
            "cross; 2xATR stop, 3xATR chandelier trail, 60-bar max hold."
        ),
        source_name="Stochastic RSI (Chande & Kroll)",
        source_url="https://blockspot.io/what-is-stochastic-rsi/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
