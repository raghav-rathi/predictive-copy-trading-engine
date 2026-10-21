"""Holy Grail engine: registration + re-exports."""
from strategies.lbr_holy_grail import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Holy Grail",
        slug="lbr_holy_grail",
        description=(
            "Linda Raschke's Holy Grail: first pullback touch of the 20-bar "
            "EMA in a strong, rising-ADX trend; buy-stop above the touch "
            "bar's high, exit on a close through the average or ADX fade."
        ),
        source_name="Holy Grail (Linda Raschke, Street Smarts)",
        source_url="https://www.tradingsetupsreview.com/the-holy-grail-trading-setup/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
