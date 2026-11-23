"""VWAP session breakout risk config.

Intraday system: the trade is a session-VWAP breakout, so the
stop is the 2xATR(14) harness backstop and the signal-level exit
(a close back through VWAP) is the real exit. No trail (a trail
would fight the VWAP-reclaim exit) and no target (there is no
opposite band target in a breakout system — the exit is the
VWAP reclaim). 24-bar (~one session) max hold: a breakout that
has not run within its own session is not a session breakout.
1% risk per trade, 3x leverage cap. Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# One full UTC session (24 hourly bars) before the first signal
# can be trusted — early-session bands are built from few bars.
WARMUP = 24
