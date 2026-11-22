"""ClucHAnix risk config.

The source's risk management is a profit-stepped CUSTOM stoploss,
not an ATR stop, and it cannot be expressed in RiskConfig:

    sell_params pHSL=-0.15, pPF_1=0.02, pSL_1=0.02, pPF_2=0.05,
    pSL_2=0.04 — hard stop at -15% of entry, then the stop locks
    in +2% once profit passes +2%, interpolates to +4% at +5%
    profit, and trails profit 1:1 above +5%.

Closest faithful mapping on 1h bars: a 6xATR(14) hard stop with a
6xATR chandelier trail. 1h ATR(14) on BTC/ETH/HYPE in this window
is roughly 1.5-2.5% of price, so 6xATR is ~9-15% — the same
order as the source's -15% hard stop — and the chandelier trail
approximates the source's profit lock-in (it only ever ratchets
the stop up, never down). The DCA rebuy (ClucDCA, -8% rebuy) is
NOT implemented: the harness is single-position, no averaging.
max_hold 72 bars (~3 days): the source is a 1m scalper (average
trade ~50 min); on 1h bars the same logic must be given room to
resolve, but a pullback entry that has not resolved in three
days is stale. 1% risk per trade, 3x leverage cap (house
standard). Long/short symmetric (short side is a builder-added
mirror of the long-only source; see CALIBRATION.md).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=6.0,
    trail_atr_mult=6.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

# BB(40) + ROCR(168) spin-up, with margin.
WARMUP = 200
