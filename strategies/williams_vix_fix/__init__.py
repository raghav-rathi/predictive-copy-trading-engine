"""Williams VIX Fix: registration + re-exports."""

from strategies.williams_vix_fix import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Williams VIX Fix",
        slug="williams_vix_fix",
        description="Larry Williams VIX Fix: WVF = 100*(highest close over 22 bars - low)/highest close over 22 bars; a green flash (fear spike) is WVF at/above its SMA(20)+2*std(20) upper band or at/above 0.85*max WVF over trailing 50 bars. An inverted WVF (100*(high - lowest close over 22)/lowest close over 22) has its own bands and flashes. Long on a green-flash transition, short on an inverted-flash transition; exit on the opposite flash, plus the harness stop/trail.",
        source_name="Larry Williams, 'The VIX Fix' (Active Trader, Dec 2007)",
        source_url="https://doc.stocksharp.com/en/api-examples/0454_Williams_Vix_Fix",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
