"""Breakout-retest risk config.

The edge (such as it is) is the retest entry itself: a throwback
touch that holds. So the hard stop is tight — 1.0xATR under the
retest level — matching the canon "tight stop under the retest
low"; a retest that immediately loses 1 ATR is a failed polarity
flip, not a position worth nursing. The measured-move target is
2.0xATR (approx 2R). No chandelier trail: exits are
signal-driven (level lost) or the fixed 2R target, plus a 96-bar
(~4 day) max hold so a drifting position does not tie up
capital. Both directions allowed — the polarity principle is
symmetric. 1% risk/trade, 3x leverage cap, standard 0.045% +
0.01% costs.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.0,
    trail_atr_mult=None,
    target_atr_mult=2.0,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # range(20) + window(20) spin-up, ATR settle, with margin
