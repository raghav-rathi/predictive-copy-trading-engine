"""CVD divergence engine: registration + re-exports."""

from strategies.cvd_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="CVD Divergence",
        slug="cvd_divergence",
        description=(
            "Cumulative Volume Delta from close-location volume "
            "approximation; 10-bar price pivots; long on bullish regular "
            "divergence (price lower low vs CVD higher low within 60 bars), "
            "short on bearish divergence; exits on opposite divergence or "
            "3xATR trailing stop."
        ),
        source_name="TradingView script: Cumulative Volume Delta with Divergence (zjvhcYEe)",
        source_url="https://fr.tradingview.com/script/zjvhcYEe-Cumulative-Volume-Delta-with-Divergence/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
