"""Prior-week range breakout: registration + re-exports."""

from strategies.weekly_pivot_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Prior-Week Range Breakout",
        slug="weekly_pivot_breakout",
        description="Prior-week range breakout (UTC week starting Monday 00:00 UTC): long on a close above the prior complete week's high, short on a close below its low; exit on a close back inside the prior-week range or the opposite breakout. Levels update only at week boundaries; plus the harness stop/trail.",
        source_name="Prior-week high/low breakout (classic weekly pivot range)",
        source_url="https://www.investopedia.com/terms/b/breakout.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
