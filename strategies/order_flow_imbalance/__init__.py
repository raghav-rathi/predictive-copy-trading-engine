"""Order-flow imbalance: registration + re-exports."""

from strategies.order_flow_imbalance import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Order Flow Imbalance",
        slug="order_flow_imbalance",
        description=(
            "Bar-delta proxy of footprint delta: per-bar signed "
            "volume delta = v * (c - o) / max(h - l, eps), "
            "clipped to [-v, v]; imbalance = 5-bar rolling sum "
            "of delta / 5-bar rolling sum of volume, in [-1, 1]. "
            "Long when imbalance crosses above +0.25 while close "
            "> EMA(20); short on the mirror below -0.25. Exit "
            "when imbalance crosses back through 0. 2xATR stop, "
            "2.5xATR trail, 120-bar max hold."
        ),
        source_name="Footprint charts and cumulative delta (order-flow delta: aggressive buys minus aggressive sells)",
        source_url="https://nordfx.com/useful-articles/footprint-charts-cumulative-delta-order-flow-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
