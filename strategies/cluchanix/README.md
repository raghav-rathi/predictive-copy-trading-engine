# ClucHAnix (Freqtrade, crypto-native)

A faithful port of the ClucHAnix strategy from
[ssssi/freqtrade_strs](https://github.com/ssssi/freqtrade_strs)
(ClucHAnix/ClucHAnix.py), run on 1h bars instead of its native
1m, with the repository's published hyperopt constants unchanged.

## Mechanism

1. **Heikin Ashi candles** smooth the raw OHLC.
2. **Bollinger Bands (40, 2σ)** on the Heikin Ashi typical price
   `(ha_high + ha_low + ha_close) / 3`.
3. **EMA(3) / EMA(50)** on the HA close.
4. **Fisher-transformed RSI(14)**: `fisher = tanh(0.1 * (rsi - 50))`,
   RSI on the regular close.
5. **ROCR(28)** on the HA close, and **ROCR(168)** — the source's
   1h informative ROCR(168); on 1h bars the 168-bar lookback IS
   the 1h informative series (7 days of 1h closes).

### Long entry

ROCR(168) > 0.54904 AND (primary OR alternative):

- **Primary** (pullback to the lower band): prior lower band > 0,
  BBDelta > HA close × 0.01965, close-delta > HA close × 0.00556,
  tail < BBDelta × 0.95089, HA close < prior lower band, and HA
  close ≤ prior HA close.
- **Alternative**: HA close < EMA(50) AND HA close < 0.00799 ×
  lower band. At the published constant this path is effectively
  dormant (0.8% of the band is below any positive price); it is
  implemented as written, not repaired — see CALIBRATION.md.

### Long exit (source sell trend)

Fisher > 0.38414 AND two consecutive lower HA highs AND HA close
≤ prior HA close AND EMA(3) > HA close AND HA close × 1.07634 >
BB mid AND volume > 0.

### Short side

Builder-added mirror of the long-only source: primary entry
across the **upper** band (HA close > prior upper band, rising HA
close, upper tail < BBDelta × 0.95089), ROCR gate reciprocated
(ROCR(168) < 1/0.54904), alternative across the upper band, exit
mirrors the sell trend (Fisher < −0.38414, two rising HA lows,
HA close × 1.07634 < BB mid).

## Risk

The source's profit-stepped custom stoploss (hard stop −15%,
lock in +2% at +2% profit, +4% at +5% profit, trail profit 1:1
above +5%) cannot be expressed in `RiskConfig`; it is mapped to
a 6×ATR(14) stop with a 6×ATR chandelier trail (≈9–15% on 1h
crypto, the same order as the −15% hard stop), 72-bar max hold,
1% risk per trade, 3× leverage cap. The DCA rebuy (ClucDCA) is
not implemented — the harness is single-position. WARMUP = 200.

Source: ssssi/freqtrade_strs — ClucHAnix
(https://deepwiki.com/ssssi/freqtrade_strs/5.2-cluchanix-strategy).
All entry/exit constants were pulled verbatim from the repo's
`ClucHAnix.py` buy_params / sell_params on 2026-11-22.
