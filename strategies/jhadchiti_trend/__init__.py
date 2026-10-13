"""jhadchiti trend engine: registration + re-exports."""

from strategies.jhadchiti_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="jhadchiti trend (55-bar breakout + BTC regime + funding + momentum)",
        slug="jhadchiti_trend",
        description=(
            "55-period close breakout gated by BTC SMA(200) regime, "
            "hourly funding <= 20bps/8h, and coin-vs-BTC 30-bar momentum; "
            "exit on 20-period channel cross; 2xATR(20) stop, 0.75% risk."
        ),
        source_name="jhadchiti crypto-trading-system (live system, 2026)",
        source_url="https://github.com/jhadchiti/crypto-trading-system",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
