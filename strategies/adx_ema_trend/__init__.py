"""ADX EMA Trend: registration + re-exports."""

from strategies.adx_ema_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ADX EMA Trend",
        slug="adx_ema_trend",
        description="EMA(20)/EMA(50) crossover with ADX(14) filter: long on a cross up with ADX > 25 and +DI > -DI, short on a cross down with ADX > 25 and -DI > +DI; exit on the reverse cross or ADX < 20, plus the harness stop/trail.",
        source_name="EMA crossover swing strategy (Trading Compendium) / EMA crossover and ADX (ForexBite)",
        source_url="https://tradingcompendium.com/en/trading-strategies/ema-crossover-swing-strategy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
