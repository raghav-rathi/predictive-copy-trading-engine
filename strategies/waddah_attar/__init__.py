"""Ahmad Waddah Attar's Waddah Attar Explosion: registration + re-exports."""

from strategies.waddah_attar import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Waddah Attar Explosion",
        slug="waddah_attar",
        description=(
            "Waddah Attar Explosion: hist = 150*(EMA(C,20)-EMA(C,40) delta), "
            "explosion line = 2x stdev(hist, 20), dead zone = 3.7x ATR(100); "
            "long when hist > 0, rising, above a rising explosion line, "
            "both above the dead zone (mirror for shorts); exit when the "
            "histogram falls back under the explosion line; 2xATR stop, "
            "3xATR trail, 200-bar max hold."
        ),
        source_name="Waddah Attar Explosion (ctrader.com, author's own entry/exit rules)",
        source_url="https://ctrader.com/products/3133",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
