"""EMA ribbon alignment + expansion: registration + re-exports."""

from strategies.ema_ribbon import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EMA Ribbon",
        slug="ema_ribbon",
        description="EMA ribbon (8/13/21/34/55): enter long on the bar full bullish alignment first appears with close above EMA8 and the ribbon spread above 0.2%; mirror for shorts. Exit when alignment breaks (EMA8 vs EMA21) or close crosses EMA34.",
        source_name="AlgoMax — Moving Average Ribbon: Read Trend Strength at a Glance",
        source_url="https://algomax.ai/blog/moving-average-ribbon-strategy-explained",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
