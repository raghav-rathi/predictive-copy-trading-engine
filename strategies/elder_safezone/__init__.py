"""Alexander Elder SafeZone: registration + re-exports."""

from strategies.elder_safezone import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder SafeZone",
        slug="elder_safezone",
        description=(
            "Alexander Elder's SafeZone trailing-stop system on 1h bars. "
            "Trend = EMA(22); the long SafeZone line is the highest low "
            "of the last 10 bars minus 2.5x the average counter-trend "
            "penetration (short line mirrored off the highs). LONG on a "
            "close crossing above EMA(22) while above the SafeZone long "
            "line; exit when price closes below the line. 2.0xATR stop, "
            "2.5xATR chandelier trail, 96-bar (~4-day) max hold."
        ),
        source_name="Alexander Elder SafeZone (Come Into My Trading Room, 2002)",
        source_url="https://www.incrediblecharts.com/indicators/safezone.php",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
