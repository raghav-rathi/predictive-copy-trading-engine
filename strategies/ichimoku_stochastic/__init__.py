"""Ichimoku + Stochastic: registration + re-exports.

Ichimoku Kinko Hyo (Goichi Hosoda) + Stochastic Oscillator
(George Lane): LONG when price is above the cloud, Tenkan is
above Kijun, and %K crosses above %D while %K < 30; SHORT on
the mirror. Exit on the opposite Stochastic cross or a close
back into/through the cloud. 2xATR(14) stop, 3xATR chandelier
trail, 120-bar max hold.
"""

from strategies.base import StrategySpec
from strategies.ichimoku_stochastic import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ichimoku + Stochastic",
        slug="ichimoku_stochastic",
        description=(
            "Ichimoku cloud (9/26/52) trend filter with a Stochastic "
            "(14,3,3) cross trigger: LONG when close is above the "
            "cloud top and Tenkan > Kijun and %K crosses above %D "
            "while %K < 30; SHORT on the mirror (close below cloud "
            "bottom, Tenkan < Kijun, %K crosses below %D while "
            "%K > 70). Exit on the opposite Stochastic cross or a "
            "close back inside/through the cloud. 2xATR(14) stop, "
            "3xATR chandelier trail, 120-bar max hold."
        ),
        source_name="Ichimoku Kinko Hyo (Goichi Hosoda) + Stochastic Oscillator (George Lane)",
        source_url="https://www.investopedia.com/terms/i/ichimoku-cloud.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
