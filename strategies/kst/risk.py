"""Know Sure Thing (KST) risk config.

The KST signal-line cross is a smoothed momentum turn, so the trade
runs as a swing: the 2xATR hard stop covers reversal shock, the 3xATR
chandelier trail manages the swing, and there is no fixed target
because the opposite cross is the natural exit. Max hold 200 bars
keeps a dead position from camping once the KST goes flat near its
signal line. The sign-gate on entries (longs only while KST < 0)
means entries happen earlier in the turn, which slightly improves
the reward-to-stop geometry versus ungated late crosses.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=200,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# ROC(30) + 15-bar SMA + 9-bar signal spin-up: 30 + 14 + 8 = 52,
# rounded up with margin
WARMUP = 80
