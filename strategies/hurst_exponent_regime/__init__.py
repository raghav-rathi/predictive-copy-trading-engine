"""Hurst exponent regime switch: registration + re-exports."""

from strategies.hurst_exponent_regime import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Hurst Exponent Regime Switch",
        slug="hurst_exponent_regime",
        description="Rolling Hurst exponent (R/S, 200-bar window, scales 10/20/40/100) switches between trend and mean-reversion modes with 3-bar hysteresis: H>0.55 trend mode trades EMA(20/50) crosses, H<0.45 reversion mode fades RSI(14) extremes to the 50 line, 0.45-0.55 no entries; exits are the mode's opposite signal or invalidation (close through EMA(50) / RSI crossing 50), plus the harness stop/trail.",
        source_name="Hurst exponent market-regime detection (DT Systems; Nomena)",
        source_url="https://dtsystems.dev/blog/market-regime-detection-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
