"""Tom DeMark TD Combo engine: registration + re-exports."""

from strategies.td_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TD Combo (DeMark)",
        slug="td_combo",
        description=(
            "9-bar consecutive setup (close vs close[4]) then 13-bar "
            "countdown (close<=low[2], lower lows/closes); enter on "
            "countdown 13; exit on price flip or 24-bar time stop; "
            "1xATR stop."
        ),
        source_name="Tom DeMark, The New Science of Technical Analysis — TD Combo countdown rules",
        source_url="https://www.theforex7.com/trade/td-combo-713/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
