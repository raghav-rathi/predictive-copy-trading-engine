"""ICT Inducement -> Sweep -> MSS Entry: registration + re-exports."""

from strategies.ict_inducement_sweep import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ICT Inducement → Sweep → MSS Entry",
        slug="ict_inducement_sweep",
        description=(
            "Full ICT sequence: order block from a displacement leg, "
            "inducement swing, sweep through the inducement into the "
            "POI, market-structure shift plus displacement with a "
            "fair-value gap, entry at the 70.5% OTE retracement "
            "(24-bar expiry). Stop beyond the POI (~2xATR), target "
            "~2R (4xATR), 72-bar max hold. No killzone filter."
        ),
        source_name="ForexMT4Indicators — Inducement in ICT Trading Explained",
        source_url="https://forexmt4indicators.com/what-is-inducement/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
