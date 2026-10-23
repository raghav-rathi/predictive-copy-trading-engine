"""Pin bar reversal risk config.

The canon: the stop goes just beyond the rejection tail (1xATR —
the tail itself is typically 0.5–1.0xATR on 1h crypto bars, so 1xATR
keeps the stop outside it without strangling the trade), and the
take-profit is the textbook 2R (2xATR) for a minimum 1:2
risk/reward.  No trail: pin-bar reversals are mean-reversion
swings, not trend legs — the 2R target is the exit, and a 48-bar
(2-day) max hold cuts off the stalled ones.  Both sides allowed:
the pattern is symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.0,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 40  # swing(5) + ATR(14) spin-up, with margin
