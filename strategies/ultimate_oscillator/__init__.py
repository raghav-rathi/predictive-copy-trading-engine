"""Larry Williams' Ultimate Oscillator divergence (1985)."""

from strategies.ultimate_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ultimate Oscillator Divergence",
        slug="ultimate_oscillator",
        description=(
            'Larry Williams\' Ultimate Oscillator (7/14/28 buying-pressure, 4:2:1 weights), Williams\' three-step divergence method mechanized: confirmed-pivot price/oscillator divergence with the oscillator below 30 (above 70 for shorts), entry on the breakout past the divergence extreme, exit when the oscillator crosses 70/30. 1.5xATR stop, 2xATR chandelier trail, 96-bar max hold.'
        ),
        source_name="Ultimate Oscillator (Larry Williams)",
        source_url="https://en.wikipedia.org/wiki/Ultimate_oscillator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
