"""Chande Momentum Oscillator: registration + re-exports."""

from strategies.chande_momentum import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande Momentum Oscillator",
        slug="chande_momentum",
        description="Tushar Chande CMO(14): 100*(sum of up-close moves - sum of down-close moves)/(sum of up-close moves + sum of down-close moves) over 14 bars. Long on a cross up through -50, short on a cross down through +50; exit on the opposite cross, plus the harness stop/trail.",
        source_name="Tushar Chande, The New Technical Trader (1994) / TrendSpider CMO",
        source_url="https://trendspider.com/learning-center/chande-momentum-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
