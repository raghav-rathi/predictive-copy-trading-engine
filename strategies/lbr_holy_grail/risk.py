"""Holy Grail risk config.

The Grail is a tight pullback entry with a fast verdict: either the
trend resumes from the touch or the setup is wrong. The 2xATR hard
stop sits beyond the touch bar's extreme (a close back through the
average already exits via signal), and the 3xATR chandelier trail
banks the resumed-trend legs that are the whole point of the setup --
Grail trades are meant to catch the next impulse, not to scalp the
bounce. A 100-bar max hold (~4 days) closes out positions that drift
sideways after entry without ever triggering the ADX-fade or
average-cross exits.

WARMUP=60: ADX(14) needs ~28+ bars to stabilize and the rising-ADX
comparison plus EMA(20) spin-up need margin on top.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=100,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60
