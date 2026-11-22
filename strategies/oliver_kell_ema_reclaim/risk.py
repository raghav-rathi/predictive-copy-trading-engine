"""Oliver Kell 20-EMA Reclaim risk config.

Source mechanics: hard stop 3% below entry (or under the
pullback low); exit on a close below the 20 EMA.

DEVIATION (documented, see CALIBRATION.md): RiskConfig expresses
stops only as a multiple of ATR, not as a fixed percentage, so
the 3% hard stop is approximated with 2xATR(14) — on 1h crypto
bars ATR(14) is typically ~1-1.5% of price, so 2xATR lands in
the 2-3% band the source intends. The "under the pullback low"
alternative stop is not expressible in RiskConfig and is not
used; the signal-level exit (close below the 20 EMA) is kept.
No trail, no target. Max hold 336 bars (~14 days) fits the
source's multi-day-to-multi-week swing hold; a reclaim that has
not run in two weeks is not the trade.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=336,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 210  # 200-bar SMA + margin
