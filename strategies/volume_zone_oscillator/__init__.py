"""Volume Zone Oscillator: registration + re-exports."""

from strategies.volume_zone_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume Zone Oscillator",
        slug="volume_zone_oscillator",
        description="Khalil & Steckler VZO (TASC 2011): signed-volume EMA ratio bounded [-100, +100], traded only with EMA(60)/ADX(14) trend context — long on a VZO cross above -40 (or above 0 after a pullback that never reached -40) in an uptrend, short on the mirror in a downtrend; exit on a VZO cross back through 0 or a close through EMA(60).",
        source_name="Walid Khalil & David Steckler — Fine-Tuning Trades with the Volume Zone Oscillator (TASC, June 2011)",
        source_url="https://www.luxalgo.com/library/concept/volume-zone-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
