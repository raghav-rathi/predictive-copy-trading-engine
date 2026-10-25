"""ATR channel breakout: registration + re-exports."""

from strategies.atr_channel import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ATR Channel Breakout",
        slug="atr_channel",
        description=(
            "Volatility-adjusted breakout: long on a close above SMA(20) + "
            "1.5xATR(14), short on a close below SMA(20) - 1.5xATR(14), exit "
            "on a close back through the midline. 2xATR stop, 3xATR trail, "
            "120-bar max hold."
        ),
        source_name="ATR bands / volatility channel (Wilder ATR; Murphy, Technical Analysis of the Financial Markets)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
