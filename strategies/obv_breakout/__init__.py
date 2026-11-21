"""On-Balance Volume Breakout: registration + re-exports."""

from strategies.obv_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="On-Balance Volume Breakout",
        slug="obv_breakout",
        description="Joseph Granville's On-Balance Volume breakout: long when OBV closes above its prior-20-bar high (transition only), short when it closes below its prior-20-bar low; exits on the opposite prior-20-bar OBV extreme, plus the harness stop/trail.",
        source_name="Joseph Granville, On-Balance Volume (Investopedia)",
        source_url="https://www.investopedia.com/terms/o/onbalancevolume.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
