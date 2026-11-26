"""ICT Optimal Trade Entry (OTE) engine: registration + re-exports."""

from strategies.ict_ote_entry import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ICT Optimal Trade Entry",
        slug="ict_ote_entry",
        description=(
            "ICT Optimal Trade Entry: a 20-bar swing liquidity "
            "sweep, a >=1.5x ATR displacement breaking market "
            "structure, then entry on a retracement into the "
            "62-79% OTE zone of the leg (70.5% midline); "
            "invalidation beyond 100% of the leg, 24-bar setup "
            "expiry; 2xATR stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="ICT Optimal Trade Entry — tradingdocs / orderblock",
        source_url="https://tradingdocs.vercel.app/en/ict/ote",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
