"""Negative-Funding Fade: registration + re-exports."""

from strategies.funding_fade import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Negative-Funding Fade",
        slug="funding_fade",
        description=(
            "LONG ONLY. Long the perp on the bar funding turns negative "
            "(shorts paying longs = crowded-short sentiment), hold 8 "
            "hours, exit. Jlabs' 8h hold since 2020: Sharpe 0.84, "
            "+227.67% total, max drawdown -14.77%, 14% time in market. "
            "Funding series merged from the local data/funding/ cache "
            "(fetch_funding.py, Hyperliquid fundingHistory); 2xATR stop "
            "as a risk overlay, 8-bar max hold."
        ),
        source_name="Jlabs Digital — Dissecting Funding Rate model",
        source_url="https://typefully.com/jlabsdigital/dissecting-funding-rate-model-BGOoArs",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
