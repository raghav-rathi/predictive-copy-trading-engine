"""StatOasis Rule 4 risk config.

The source has NO indicator exit and NO stop — only the fixed
10-bar time exit. The harness therefore enforces the time exit
twice over (signals.py state machine + max_hold_bars=10). The
stop is a roomy 2xATR(14) purely as catastrophic protection;
trailing is OFF (a trail would fight the fixed-hold thesis by
cutting winners short before the 10 bars elapse) and there is
no target. 1% risk per trade, 3x leverage cap (house standard).
Long/short symmetric (short side is a builder-added mirror of
the long-only source; see CALIBRATION.md).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=10,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# 120h return lookback + indicator spin-up, with margin.
WARMUP = 150
