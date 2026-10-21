"""Klinger Volume Oscillator risk config.

The KVO/signal cross does the trade management (exits on the opposite
cross), so there is no fixed target — the 2xATR hard stop covers
gap/reversal shock and a 3xATR chandelier trail locks in extended
volume-driven trends. Volume-force breakouts on 1h bars can run
multi-day trends, hence the long 150-bar max hold. Shorts are allowed:
volume force works symmetrically (a -1 trend on high volume is just
as meaningful as +1). allow_longs/allow_shorts both True — the
oscillator has no structural long bias.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=3.0,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # EMA(55) spin-up for the slow leg, with margin
