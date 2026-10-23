"""WaveTrend Oscillator — LazyBear's classic reversal oscillator, ported as a
signal engine for 1h crypto perps.

Formula (LazyBear's canonical Pine Script release):
    ap  = (h + l + c) / 3
    esa = EMA(ap, 10)
    d   = EMA(abs(ap - esa), 10)
    ci  = (ap - esa) / (0.015 * d)      # guarded: ci = 0 when d == 0
    wt1 = EMA(ci, 21)                    # "tci" in the Pine source
    wt2 = SMA(wt1, 4)

Signals (canonical LazyBear cross-in-zone rules, ±53 zones, ±60 extremes):
    long_entry  = crossed_above(wt1, wt2) & (wt1.shift(1) < -53)
    short_entry = crossed_below(wt1, wt2) & (wt1.shift(1) > 53)
    long_exit   = crossed_below(wt1, wt2) | (wt1 > 60)
    short_exit  = crossed_above(wt1, wt2) | (wt1 < -60)

Risk: 1.5xATR stop, 2xATR chandelier trail, 72-bar (~3-day) max hold,
1% risk/trade, 3x leverage cap, longs + shorts. Paper/backtest only —
never wired to live execution.
"""

from strategies.wave_trend import indicators, signals, risk  # noqa: F401


from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="WaveTrend Oscillator",
        slug="wave_trend",
        description=(
            'LazyBear\'s WaveTrend oscillator: wt1 = EMA((ap - esa) / (0.015 * d), 21), wt2 = SMA(wt1, 4). Long when wt1 crosses above wt2 below the -53 oversold line; short mirror above +53. Exits on the opposite cross or the +/-60 extremes. 1.5xATR stop, 2xATR chandelier trail, 72-bar max hold.'
        ),
        source_name="WaveTrend (LazyBear)",
        source_url="https://www.fmz.com/lang/en/strategy/449714",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
