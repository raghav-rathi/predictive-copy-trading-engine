"""ICT/SMC order-block retest: registration + re-exports."""

from strategies.order_block_retest import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Order Block Retest",
        slug="order_block_retest",
        description=(
            "ICT/SMC order block: a 3-bar move >= 1.5xATR(14) marks "
            "displacement; the order block is the range of the last "
            "opposite-color candle before the leg. Enter in the "
            "displacement direction when a later close re-enters the "
            "block (block at most 48 bars old). Exit on block "
            "violation or a new opposite displacement. 2xATR stop, "
            "2xATR chandelier trail, 96-bar max hold."
        ),
        source_name="ICT (Inner Circle Trader) Smart Money Concepts — order blocks",
        source_url="https://www.youtube.com/@InnerCircleTrader",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
