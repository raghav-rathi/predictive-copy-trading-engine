"""BTC Breakout Trend Climber: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.btc_breakout_trend_climber import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="BTC Breakout Trend Climber",
        slug="btc_breakout_trend_climber",
        description=(
            "Long/short breakout trend system: LONG when close breaks "
            "above the prior-600-bar (25-day) highest high or above "
            "the upper Bollinger Band (50, 2.1 sigma, EMA mid); mirror "
            "for SHORT. ATR-staged exit mapped to a 3.5xATR(10) stop "
            "with an 11.0xATR(10) chandelier trail; opposite breakout "
            "exits. Long-only in the source, mirrored for shorts."
        ),
        source_name="QuantConnect community backtest — BTC Breakout Trend Climber",
        source_url="https://www.quantconnect.com/terminal/cache/embedded_backtest_ad553ee3018fa48c5a0395a33ba8b2dd.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
