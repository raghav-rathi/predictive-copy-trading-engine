"""ATR-percentile volatility regime switch: registration + re-exports."""

from strategies.volatility_regime_switch import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volatility Regime Switch",
        slug="volatility_regime_switch",
        description="ATR(14) percentile rank over 100 bars switches between expansion and compression: above the 60th percentile trade Donchian(20) breakouts (close beyond the prior 20-bar high/low excluding the current bar), below the 40th percentile fade Bollinger(20, 2) extremes back to the mid; 40-60 no entries; exits are the channel midpoint / opposite break in expansion and the Bollinger mid in compression, plus the harness stop/trail.",
        source_name="Momentum vs mean-reversion strategies (ForTraders)",
        source_url="https://fortraders.com/blog/momentum-vs-mean-reversion-strategies-for-challenges",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
