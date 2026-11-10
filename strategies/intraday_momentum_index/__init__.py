"""Tushar Chande's Intraday Momentum Index: registration + re-exports."""

from strategies.intraday_momentum_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Intraday Momentum Index",
        slug="intraday_momentum_index",
        description="Chande's IMI: RSI on open-to-close moves — 100 * sum of intraday gains / (sum of gains + sum of losses) over 14 bars. Long on IMI crossing up through 30, short on crossing down through 70, exit on the opposite extreme cross.",
        source_name='Tushar Chande — "The New Technical Trader" (Intraday Momentum Index)',
        source_url="https://doc.stocksharp.com/en/topics/api/indicators/list_of_indicators/intraday_momentum_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
