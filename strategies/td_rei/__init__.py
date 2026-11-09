"""DeMark Range Expansion Index: registration + re-exports."""

from strategies.td_rei import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DeMark Range Expansion Index",
        slug="td_rei",
        description="DeMark TD REI(5): 100 x 5-bar sum of the gated high/low momentum vs two bars earlier over the 5-bar sum of absolute momentum, bounded to [-100, +100]. Long when REI crosses above -60 from below; short when it crosses below +60 from above; exit on the opposite extreme cross.",
        source_name="Tom DeMark — The New Science of Technical Analysis (1994), ch. 4; AmiBroker AFL Formula Library",
        source_url="https://www.amibroker.com/newsletter/02-2000.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
