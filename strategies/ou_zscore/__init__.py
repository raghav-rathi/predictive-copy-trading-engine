"""OU Half-Life Z-Score Mean Reversion: registration + re-exports."""

from strategies.ou_zscore import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="OU Half-Life Z-Score Mean Reversion",
        slug="ou_zscore",
        description=(
            "Deviation dev = log(close) - SMA(log(close), 50). Each bar "
            "fits AR(1) on the trailing 100 dev values (rolling "
            "cov/var, causal) and converts the slope to a half-life "
            "HL = -ln2/theta. Long when z = dev/std(dev,50) < -2 AND "
            "theta < 0 with 5 <= HL <= 120; exit when z >= 0; short "
            "mirrored (z > 2, exit z <= 0). 2.5xATR stop, 200-bar max "
            "hold, no target, no trail."
        ),
        source_name="OU half-life mean reversion (luxalgo.com)",
        source_url="https://www.luxalgo.com/blog/mean-reversion-strategies-for-algorithmic-trading/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
