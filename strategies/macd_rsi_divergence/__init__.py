"""MACD divergence: registration + re-exports.

Name note: the slug is ``macd_rsi_divergence`` but the shipped
system is MACD-only for both sides, per the build spec — RSI
divergence was not implemented (RSI(14) is computed for
inspection only). See README.md.
"""

from strategies.base import StrategySpec
from strategies.macd_rsi_divergence import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD + RSI Divergence (MACD-only)",
        slug="macd_rsi_divergence",
        description=(
            "Regular MACD-histogram divergence on confirmed (+/-2-bar) "
            "price pivots: LONG on a lower confirmed pivot low with a "
            "higher histogram at the pivot (vs the previous pivot low) "
            "and a rising histogram on the confirmation bar; SHORT on "
            "the mirror. Exit on a histogram zero-cross or the opposite "
            "divergence. 2xATR(14) stop, 120-bar max hold. MACD-only — "
            "RSI divergence was NOT implemented, despite the slug. "
            "Entries lag the turn by design (two pivots + 2-bar "
            "confirmation)."
        ),
        source_name="Gerald Appel (MACD) + classic divergence literature (Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://thepatternsite.com/Divergence.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
