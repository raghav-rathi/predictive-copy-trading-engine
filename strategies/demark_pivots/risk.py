"""Tom DeMark pivot risk config.

The spec's stop sits beyond the opposite level plus 0.5xATR: the
stop for a long is below S1 + 0.5xATR, for a short above R1 +
0.5xATR. The harness only supports a stop expressed as a multiple
of ATR from the entry price, so the level distance is folded in:
on 1h crypto the R1/S1 band is typically ~1xATR wide, so a
1.5xATR stop approximates "beyond the opposite level + 0.5xATR"
(1xATR of band width + 0.5xATR of clearance). It is an
approximation, not the exact level stop — the signal exit (close
back inside the band) is what normally gets a failed breakout out.

Likewise the spec's target is 1.5x the daily range. The daily
range over a 24-bar "day" runs roughly 2x the hourly ATR(14) on
these coins, so the target is approximated as 3.0xATR(14)
(1.5 x ~2xATR). Both mappings are documented here because the
harness cannot express level-based stops/targets directly.

Max hold is 24 bars (~1 day): a pivot breakout that has not paid
within one synthetic day is stale.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,   # ~ opposite level + 0.5xATR (see docstring)
    trail_atr_mult=None,
    target_atr_mult=3.0,  # ~ 1.5x daily range (see docstring)
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 48  # 24-bar day + 24 bars for the levels to roll + margin
