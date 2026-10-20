"""SSL Channel (SMA high/low channel): registration + re-exports."""

from strategies.ssl_channel import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SSL Channel",
        slug="ssl_channel",
        description=(
            "SSL Channel: ssl_up = SMA(High,10), ssl_dn = SMA(Low,10); "
            "bullish when close > ssl_up, bearish when close < ssl_dn, "
            "prior state held in between; long on the flip to bullish, "
            "short on the flip to bearish, exits on the opposite flip; "
            "2xATR stop, 200-bar max hold."
        ),
        source_name="SSL Channel strategy (fmz.com)",
        source_url="https://www.fmz.com/strategy/443990",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
