"""Multi-Timeframe EMA Agreement filter: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.multi_timeframe_ema_agreement import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Multi-Timeframe EMA Agreement filter",
        slug="multi_timeframe_ema_agreement",
        description=(
            "BotLab's sole surviving filter of 60 tested: a 1h "
            "EMA(9)/EMA(21) cross is taken only when the 4h EMA(9)/"
            "EMA(21) pair points the same way (4h EMAs from completed "
            "4h bars only). Exit on the opposite 1h cross. 2xATR stop, "
            "3xATR trail, 120-bar max hold."
        ),
        source_name="BotLab — Do Funding Rate and Open Interest Filters Improve a Crypto Bot?",
        source_url="https://botlab.org.uk/learn/do-funding-rate-and-open-interest-filters-improve-a-crypto-bot",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
