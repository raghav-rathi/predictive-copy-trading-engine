"""RSI pullback to EMA(50) (classic pullback system): registration + re-exports."""

from strategies.base import StrategySpec
from strategies.rsi_ema_pullback import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI pullback to EMA(50)",
        slug="rsi_ema_pullback",
        description=(
            "RSI pullback to EMA(50): in an uptrend (close above a "
            "rising EMA(50)), RSI dipping below 40 then crossing "
            "back above 40 is a long; mirror short in a downtrend "
            "on RSI above 60 crossing back below 60. Exit long on "
            "RSI 70 or close below EMA(50); exit short on RSI 30 "
            "or close above EMA(50). 2xATR(14) harness stop; "
            "120-bar max hold; 1% risk, 3x cap. The EMA filter is "
            "the only thing separating this from a falling-knife "
            "system."
        ),
        source_name="Larry Connors & Linda Raschke, Street Smarts (1995), pullback chapter",
        source_url="https://www.tradingview.com/ideas/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
