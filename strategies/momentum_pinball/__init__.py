"""Momentum Pinball engine: registration + re-exports."""

from strategies.momentum_pinball import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Raschke Momentum Pinball (LBR/RSI) system",
        slug="momentum_pinball",
        description=(
            "LBR/RSI = 3-period RSI of the 1-period ROC of close; long when "
            "the pinball flips up out of <30, short when it flips down out of "
            ">70; exit at the opposite extreme."
        ),
        source_name="Linda Raschke / Larry Connors — Momentum Pinball (Street Smarts)",
        source_url="https://www.cryptodatadownload.com/blog/posts/short-term-strategy-momentum-pinball-python/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
