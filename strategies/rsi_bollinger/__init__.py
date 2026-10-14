"""Bollinger-on-RSI engine: registration + re-exports."""

from strategies.rsi_bollinger import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bollinger Bands on RSI mean-reversion system",
        slug="rsi_bollinger",
        description=(
            "20-period Bollinger Bands (2 std) on RSI(14); long when RSI "
            "re-enters from below its lower band, short on the mirror; "
            "exit at the band midline."
        ),
        source_name="RSI + Bollinger mean-reversion (BTC mean-reversion reference)",
        source_url="https://www.tradingview.com/script/95JBkzXV-BTC-Mean-Reversion-RSI-Bollinger/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
