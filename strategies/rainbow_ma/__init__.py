"""Rainbow Moving Average: registration + re-exports."""

from strategies.rainbow_ma import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Rainbow Moving Average",
        slug="rainbow_ma",
        description="Rainbow MA: 22 EMAs from 9 to 100 periods. Long when price crosses above the whole ribbon (above every EMA) while the fastest EMA is rising; short when price crosses below the whole ribbon while the fastest EMA is falling; exit when price falls back inside the ribbon.",
        source_name="Rainbow Moving Average (22-EMA ribbon)",
        source_url="https://www.best-trading-platforms.com/trading-platform-futures-forex-cfd-stocks-nanotrader/rainbow-moving-average?page=4",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
