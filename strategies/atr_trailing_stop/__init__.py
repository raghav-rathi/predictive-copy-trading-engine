"""ATR trailing-stop trend system: registration + re-exports."""

from strategies.atr_trailing_stop import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ATR Trailing Stop",
        slug="atr_trailing_stop",
        description="Chuck LeBeau's Chandelier Exit family: the trailing stop hangs 3x ATR(14) below the highest high since the long regime started (mirrored for shorts) and only ever ratchets in the trade's favour. Long when the close crosses above the trailing stop from below (regime flips long); short when the close crosses below it from above; exit on the regime flip.",
        source_name="Chuck LeBeau — Chandelier Exit",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
