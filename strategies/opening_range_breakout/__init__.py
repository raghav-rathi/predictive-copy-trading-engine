"""Opening-range breakout engine: registration + re-exports."""

from strategies.opening_range_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Opening-Range Breakout (bake-off winner port)",
        slug="opening_range_breakout",
        description=(
            "First-4h UTC opening range; breakout entries; 3xATR target / "
            "1xATR stop (3:1); 20-bar intraday cap."
        ),
        source_name="ibrahimshere/nq-l2-scalping Strategy 020 (bake-off winner)",
        source_url="https://github.com/ibrahimshere/nq-l2-scalping/blob/HEAD/data/l2_winner_candidates.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
