"""ATR expansion breakout: registration + re-exports."""

from strategies.atr_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ATR Expansion Breakout",
        slug="atr_breakout",
        description="ATR expansion breakout: trade a close beyond the trailing 20-bar close range by 0.25xATR only when ATR is expanding (ATR > its 20-bar average) and the range is tight (width <= 2xATR); exit on a close back inside the range or when the ATR expansion fades, plus the harness stop/trail.",
        source_name="ATR breakout / volatility-expansion breakout (rule-based breakout blueprint)",
        source_url="https://www.steadypips.net/guides/breakout-trading-strategy-rule-based-blueprint/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
