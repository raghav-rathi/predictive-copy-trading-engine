"""Funding-Rate Carry engine: registration + re-exports."""

from strategies.funding_rate_carry import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Funding-Rate Carry",
        slug="funding_rate_carry",
        description=(
            "Directional funding carry: long when the 24h average "
            "funding rate crosses below -0.0000125 (deeply negative "
            "funding -- shorts pay longs, crowded shorts) and short "
            "when it crosses above +0.0000125; exit when funding "
            "normalizes past half the threshold; 2xATR stop, 3xATR "
            "trail, 168-bar max hold. Funding accrual is the edge "
            "and is accounted per trade from the local cache."
        ),
        source_name="Hyperliquid funding mechanics / SwoleCharts funding-rate tracker",
        source_url="https://swolecharts.com/hyperliquid/funding-rate",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
