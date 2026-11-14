"""GoNoGo Trend state engine: registration + re-exports."""

from strategies.gonogo_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="GoNoGo Trend",
        slug="gonogo_trend",
        description=(
            "GoNoGo Trend (Alex Cole, GoNoGo Charts) -- published-checklist "
            "reconstruction; the exact vendor formula is proprietary. "
            "Composite -5..+5 score from EMA(9/21/50) alignment, MACD "
            "histogram sign, ADX(14)>20 with +DI>-DI, Donchian(50) "
            "position, RSI(14) vs 50; states strong/weak Go, neutral "
            "(amber), weak/strong NoGo. Oscillator = MACD-hist z-score + "
            "(RSI-50)/25 clamped to +/-6. Long on transition into Go with "
            "oscillator > 0, short on transition into NoGo with oscillator "
            "< 0; exit on return to neutral or the opposite state; 2xATR "
            "stop, 3xATR trail, 150-bar max hold."
        ),
        source_name="GoNoGo Trend (Alex Cole, GoNoGo Charts)",
        source_url="https://www.gonogocharts.com/indicator/gonogo-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
