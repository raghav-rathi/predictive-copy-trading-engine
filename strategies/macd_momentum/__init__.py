"""MACD momentum engine: registration + re-exports."""

from strategies.macd_momentum import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD Histogram Momentum (EMA200-filtered)",
        slug="macd_momentum",
        description=(
            "MACD(12,26,9) histogram zero-cross entries in the EMA200 trend "
            "direction; histogram reversal exits; 2xATR stop + 3xATR trailing."
        ),
        source_name="Gerald Appel MACD (public domain)",
        source_url="https://www.investopedia.com/terms/m/macd.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
