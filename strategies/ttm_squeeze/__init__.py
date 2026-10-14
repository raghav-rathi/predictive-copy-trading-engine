"""TTM Squeeze engine: registration + re-exports."""

from strategies.ttm_squeeze import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TTM Squeeze (Carter volatility-expansion)",
        slug="ttm_squeeze",
        description=(
            "BB(20,2) inside Keltner(20-EMA,1.5xATR14) squeeze release after "
            ">=5 bars; direction from 12-bar momentum-histogram slope; exit on "
            "2 consecutive momentum-fade bars; 2xATR stop, 48-bar max hold."
        ),
        source_name="TTM Squeeze research (dexwilder/algo-lab) + Carter, Mastering the Trade Ch.11",
        source_url="https://github.com/dexwilder/algo-lab/blob/HEAD/research/volatility_expansion_strategy_research.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
