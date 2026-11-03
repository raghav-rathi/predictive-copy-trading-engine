"""DeMark Trendline Breakout: registration + re-exports."""

from strategies.demark_trendline import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DeMark Trendline Breakout",
        slug="demark_trendline",
        description=(
            "Tom DeMark TD trendlines: trendlines through the last two confirmed pivot highs (downtrend line) and last two confirmed pivot lows (uptrend line); pivots confirm with a 2-bar lag, so no lookahead. Long on close cross above the downtrend line, short on cross below the uptrend line; exits on the opposite cross."
        ),
        source_name="DeMark TD trendlines (Tom DeMark)",
        source_url="https://www.investopedia.com/terms/d/demark.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
