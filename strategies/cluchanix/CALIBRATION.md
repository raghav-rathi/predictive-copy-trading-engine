# ClucHAnix — Calibration

All parameters were fixed **a priori** from the published
`ClucHAnix.py` in ssssi/freqtrade_strs (buy_params /
sell_params, fetched 2026-11-22) and 1h-bar reasoning — there
is no in-sample sweep, so there is nothing to select on this
window. The buy/sell constants below ARE the repo's hyperopt
output (fitted by the author on other data/timeframes); they are
reproduced verbatim, not re-optimized here, and must be read as
inherited tuning, not as neutral priors.

| Parameter | Value | Rationale |
|---|---|---|
| Bollinger Bands | 40, 2σ on HA typical price | source spec (DeepWiki + code) |
| EMA fast / slow | 3 / 50 on HA close | source spec |
| RSI / Fisher | 14, `tanh(0.1*(rsi-50))` | source spec, exact formula |
| ROCR current / 1h | 28 / 168 on HA close | source spec; 168 on 1h bars IS the 1h informative series |
| `bbdelta-close` | 0.01965 | published buy_params, verbatim |
| `closedelta-close` | 0.00556 | published buy_params, verbatim |
| `bbdelta-tail` | 0.95089 | published buy_params, verbatim |
| `close-bblower` | 0.00799 | published buy_params, verbatim — see dormant-path note |
| `rocr-1h` | 0.54904 | published buy_params, verbatim — see gate note |
| `sell-fisher` | 0.38414 | published sell_params, verbatim |
| `sell-bbmiddle-close` | 1.07634 | published sell_params, verbatim |
| Custom stoploss | pHSL −0.15, PF_1 0.02 / SL_1 0.02, PF_2 0.05 / SL_2 0.04 | source sell_params; NOT expressible in RiskConfig |
| Stop / trail (mapped) | 6xATR / 6xATR | closest faithful mapping: 1h ATR ≈ 1.5–2.5% of price, so 6xATR ≈ 9–15% ≈ the −15% hard stop; chandelier approximates the profit lock-in |
| Max hold | 72 bars (~3 days) | 1m scalper logic needs room on 1h bars, but a stale pullback entry is not a trade |
| Risk | 1% / trade, 3x leverage cap | house standard |
| DCA rebuy | NOT implemented | ClucDCA's −8% rebuy needs averaging; harness is single-position |

## Documented deviations from the source

1. **Timeframe: 1m → 1h.** The source runs on 1-minute bars
   with a 1h informative timeframe. Here the whole strategy runs
   on 1h bars; the 1h ROCR(168) is computed directly on 1h HA
   closes, which is exactly the source's informative series.
   No constant was re-scaled. Consequence, visible in
   BACKTEST.md: the entry fires ~10 times in 8 months instead of
   thousands — the pattern is timeframe-native and was not
   re-tuned.
2. **ROCR gate is nearly dormant.** TA-Lib ROCR is a ratio
   (~1.0 for flat prices). The published threshold 0.54904 is
   satisfied by almost any bar, so the 1h-momentum gate barely
   filters. Implemented verbatim; the short-side mirror uses the
   reciprocal 1/0.54904 = 1.8216, symmetric around 1.0 and
   equally dormant.
3. **Alternative entry path is dormant.** `ha_close <
   0.00799 * lower` can never hold for positive prices
   (0.8% of the band). This looks like a hyperopt artifact in
   the source (the parameter was presumably meant as a ratio
   near 1.0). Implemented as written, not repaired; the short
   mirror (`ha_close > upper / 0.00799`) is dormant the same way.
4. **Custom stoploss → ATR stop/trail.** The profit-stepped
   stoploss (lock +2% at +2%, interpolate to +4% at +5%,
   trail profit 1:1 above +5%) has no RiskConfig equivalent;
   the 6xATR stop + 6xATR chandelier is the closest mapping
   (see table). It trails from the entry ATR rather than
   stepping on realized profit, so winning trades are given
   more room than the source would.
5. **Short side is a mirror, not source.** ClucHAnix is
   long-only. The short entry/exit mirror the long logic
   across the upper band / inverted Fisher; documented in
   signals.py.

No optimization was performed on the backtest window, and the
window in BACKTEST.md must not be used to tune any of these
numbers — re-scaling the 1m constants to 1h until the sample
looks good would be pure overfitting.
