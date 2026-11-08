"""RSI pullback in trend: registration + re-exports."""

from strategies.sma_rsi_pullback import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SMA-RSI Pullback",
        slug="sma_rsi_pullback",
        description="RSI pullback in trend: in an SMA50 > SMA200 uptrend, a bar whose low dips to SMA50 with RSI(14) in 40-55 arms a pullback; enter long on the first close back above SMA50 within 5 bars, exit on RSI(14) > 70 or a close below SMA200 (mirror for shorts with RSI 45-60 and exit RSI < 30).",
        source_name="Vocal Media — The RSI Pullback Strategy",
        source_url="https://vocal.media/trader/the-rsi-pullback-strategy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
