"""OBV Divergence engine: registration + re-exports."""

from strategies.obv_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="OBV Divergence",
        slug="obv_divergence",
        description=(
            "Granville On-Balance Volume divergence: bullish divergence "
            "between consecutive confirmed pivot lows (lower price low, "
            "higher OBV) enters long on the first bar after confirmation "
            "(pivot lag k=10), bearish divergence between pivot highs "
            "enters short; dedupe 15 bars; exits on the opposite pivot "
            "print or confirming opposite divergence; 1.5xATR stop, "
            "2.5xATR trail, 60-bar max hold."
        ),
        source_name="On-Balance Volume divergence (Granville, 1963)",
        source_url="https://www.ig.com/uk/learn/trading/on-balance-volume-obv-what-it-is-and-how-to-trade-it",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
