"""Funding Squeeze Reversal engine: registration + re-exports."""

from strategies.funding_squeeze_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Funding Squeeze Reversal (contrarian funding fade)",
        slug="funding_squeeze_reversal",
        description=(
            "Fade crowded perp positioning: short when 8h cumulative funding "
            "> +0.030% with elevated volume (1.5x), long when < -0.020%; "
            "confidence >= 0.45, 3x-volume violent-spike guard, reversing "
            "exits, 2xATR stop, 3xATR chandelier, 12-bar max hold."
        ),
        source_name="Funding Squeeze Reversal — beatp-bit (CoinMarketCap BNB HACK 2026)",
        source_url="https://github.com/beatp-bit/funding-squeeze-reversal",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
