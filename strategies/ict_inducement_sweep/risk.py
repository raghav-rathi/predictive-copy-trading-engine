"""ICT inducement -> sweep -> MSS -> OTE risk config.

The source ICT trade is: stop beyond the POI (past the order-block
extreme), target the next liquidity pool at ~2R. RiskConfig has a
single ATR window and ATR-based stops/targets, so the closest
faithful mapping is:

- stop 2xATR — approximates "beyond the POI" (the distance from an
  OTE entry to the OB extreme is typically ~1–2xATR on 1h bars;
  see CALIBRATION.md for the documented deviation).
- target 4xATR — exactly 2x the stop distance, i.e. the ~2R target
  of the source.
- no trail — a chandelier trail would cut the run to the 2R target
  short; the source rides to the liquidity pool.
- 72-bar max hold (~3 days): an OTE entry that hasn't reached its
  target or stop in three days is not the trade.

Long/short symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=4.0,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 100  # ATR spin-up + displacement + full sequence of structure
