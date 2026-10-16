"""Key reversal engine: registration + re-exports."""

from strategies.key_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Key reversal bar (classic, unfiltered)",
        slug="key_reversal",
        description=(
            "Classic key-reversal bar: new 20-bar high + close below the "
            "prior bar's low (bearish) or new 20-bar low + close above the "
            "prior bar's high (bullish). Calibration tested the 1.5x "
            "average-volume filter and dropped it — the unfiltered variant "
            "wins on BTC/ETH/HYPE. Entries on pattern completion; exits on "
            "the opposite pattern. 2xATR stop, 3xATR trail, 48-bar max hold."
        ),
        source_name="Key reversal bar (classic)",
        source_url="https://patternswizard.com/key-reversal-bar-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
