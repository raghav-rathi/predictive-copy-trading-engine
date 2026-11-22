"""LazyBear Squeeze Momentum: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.squeeze_momentum import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="LazyBear Squeeze Momentum",
        slug="squeeze_momentum",
        description=(
            "Squeeze release (Bollinger Bands (20, 2) expanding back "
            "outside Keltner Channels (20, 1.5xATR)) with LazyBear's "
            "linear-regression momentum: LONG on release when the "
            "momentum histogram is rising and positive, momentum is "
            "at its 100-bar low, and close is above EMA(100) and "
            "above the prior close; mirror for SHORT. Exit on the "
            "first momentum downtick (long) / uptick (short), with a "
            "2xATR(14) stop backstop."
        ),
        source_name="TradingView — Squeeze Momentum Indicator Strategy [LazyBear + PineIndicators]",
        source_url="https://th.tradingview.com/script/G40dtEbK-Squeeze-Momentum-Indicator-Strategy-LazyBear-PineIndicators/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
