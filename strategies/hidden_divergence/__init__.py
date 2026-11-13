"""RSI(14) hidden divergence: registration + re-exports."""

from strategies.hidden_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI Hidden Divergence",
        slug="hidden_divergence",
        description="RSI(14) hidden divergence (trend continuation): bullish hidden divergence — price makes a higher swing low while RSI makes a lower low at that pivot — goes long; bearish hidden divergence — price makes a lower swing high while RSI makes a higher high — goes short. Swing pivots are 5-bar (2 bars each side); exit when RSI crosses 50 against the position.",
        source_name="RSI hidden divergence (Wilder RSI, 1978; divergence taxonomy per standard technical-analysis literature)",
        source_url="https://www.investopedia.com/terms/r/rsi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
