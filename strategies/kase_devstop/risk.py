"""Kase DevStop risk config.

IMPORTANT -- the DevStop drives the exits, not the harness. The
harness RiskConfig is deliberately set WIDE so it only acts as a
disaster backstop:

    stop_atr_mult  = 6.0   -- a 6xATR(14) hard stop; the DevStop line
                              (mean DTR + 1 std, ratcheted off the
                              extreme) sits well inside this on any
                              normal bar, so in practice exits are
                              DevStop flips, not harness stops.
    trail_atr_mult = None  -- chandelier trailing OFF: a second
                              trailing stop would fight the DevStop.
    target         = None  -- no take-profit; DevStop decides.
    max_hold_bars  = 300   -- ~12 days; a DevStop position that never
                              flips in 300 bars is a stale leg.

Sizing still uses the 6xATR stop distance (1% risk per trade, 3x
leverage cap), so positions are smaller than a 2xATR strategy's --
that is the price of the wide disaster stop.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=6.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=300,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # DTR(30) band spin-up, with margin
