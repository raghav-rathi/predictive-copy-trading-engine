"""Oliver Kell 20-EMA Reclaim: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.oliver_kell_ema_reclaim import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Oliver Kell 20-EMA Reclaim",
        slug="oliver_kell_ema_reclaim",
        description=(
            "Buy the cross back above the 20 EMA after a 5-19% "
            "pullback to/below it on quiet volume, only when price "
            "is above a rising 200 SMA with rising 10/20 EMAs "
            "(Oliver Kell's pullback-to-the-20-EMA setup, 2020 U.S. "
            "Investing Championship +941%); mirror for shorts. Exit "
            "on a close back below the 20 EMA; 2xATR(14) stop "
            "approximates the source's 3% hard stop."
        ),
        source_name="Backtest Lab — He Made 941% in One Year (Oliver Kell)",
        source_url="https://www.youtube.com/watch?v=WjcZaEJHlCE",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
