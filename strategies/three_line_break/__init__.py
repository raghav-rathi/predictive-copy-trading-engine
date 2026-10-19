"""Three-line break turnaround engine: registration + re-exports."""

from strategies.three_line_break import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Three-Line Break Turnaround",
        slug="three_line_break",
        description=(
            "Three-line break chart on closes: new white line when the "
            "close exceeds the high of the last 3 lines during a black "
            "sequence (mirror for black lines); long on the -1->+1 "
            "turnaround flip, short on the +1->-1 flip, exits on the "
            "opposite flip; 2xATR stop, 60-bar max hold."
        ),
        source_name="Three-line break (TradingView support)",
        source_url="https://th.tradingview.com/support/solutions/43000502273/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
