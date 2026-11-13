"""Grid trading (range system): registration + re-exports."""

from strategies.grid_trading import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Grid Trading",
        slug="grid_trading",
        description="Classic grid trading (range system): the trailing 200-bar high/low range is split into 10 equal levels. Single-position harness approximation: long when the close falls into the bottom 20% of the grid range (buy the dip of the range), exit at the range midpoint; short when the close rises into the top 20% of the range, exit at the midpoint. The grid is recomputed causally each bar from the trailing 200 bars.",
        source_name="Grid Trading — Investopedia",
        source_url="https://www.investopedia.com/terms/g/grid-trading.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
