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

__all__ = ["indicators", "signals", "risk"]
