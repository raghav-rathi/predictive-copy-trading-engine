"""ADX Bollinger squeeze engine: registration + re-exports."""

from strategies.adx_bollinger_squeeze import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ADX Bollinger Squeeze",
        slug="adx_bollinger_squeeze",
        description=(
            "Bollinger squeeze + ADX expansion breakout: BB(20, 2.0) "
            "bandwidth at its 20-bar minimum, then a close outside the "
            "band with ADX(14) > 20; exit when the close comes back "
            "inside the bands or ADX < 15; 2xATR stop, 3xATR trail, "
            "60-bar max hold."
        ),
        source_name="John Bollinger — Bollinger Bands / Bandwidth squeeze",
        source_url="https://www.nasdaq.com/articles/rare-volatility-indicator-helps-spot-price-breakouts-2019-04-15",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
