# CVD Trend — Calibration

CVD-EMA length sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-18, same costs/sizing,
2xATR stop, 3xATR trail, 150-bar max hold). The sweep re-runs
`add_indicators(df, cvd_n=X)` only — signals and risk are unchanged.
EMA(50) price filter held fixed throughout.

| CVD EMA | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 406 | 25.9% | -$5,425 | -5.49 | 0.49 | -$13.36 |
| 10 | ETH | 384 | 27.3% | -$4,114 | -4.09 | 0.61 | -$10.71 |
| 10 | HYPE | 343 | 33.5% | -$596 | -0.34 | 0.95 | -$1.74 |
| 20 (shipped) | BTC | 303 | 29.7% | -$3,071 | -2.53 | 0.71 | -$10.14 |
| 20 (shipped) | ETH | 265 | 29.1% | -$2,355 | -2.13 | 0.74 | -$8.89 |
| 20 (shipped) | HYPE | 257 | 31.9% | -$1,262 | -0.93 | 0.87 | -$4.91 |
| 30 | BTC | 252 | 23.8% | -$3,738 | -3.43 | 0.60 | -$14.83 |
| 30 | ETH | 225 | 28.4% | -$2,482 | -2.43 | 0.68 | -$11.03 |
| 30 | HYPE | 208 | 34.1% | +$1,044 | +0.87 | 1.13 | +$5.02 |

## One-line verdict

- **n=10:** the chop setting — 1,133 trades, combined -$10,135, the
  worst of the three. A faster CVD EMA turns on noise.
- **n=30:** the least-bad combined (-$5,176) and the only green coin
  anywhere (HYPE +$1,044, PF 1.13), but BTC is worse than at n=20
  (-$3,738) and the combined figure is still deeply negative.
- **n=20 (shipped):** combined -$6,688. Kept because it was the
  a-priori default fixed in the brief, not because the sweep ranks it
  best — switching to n=30 *because* it is less bad in-sample would
  be in-sample selection on a window where every setting loses.
- The honest read: the length moves which coin loses least, not
  whether the strategy works. The close-location proxy, not the EMA
  length, is the binding limitation.

## Spec corrections vs the brief

None. The brief was implemented exactly as specified:

- Close-location proxy buy_vol=v×(c−l)/(h−l), sell_vol=v−buy_vol,
  delta=buy_vol−sell_vol, CVD=cumsum(delta) — as specified, with the
  approximation documented in README.md (flat bars split 50/50).
- Long when EMA(CVD,20) slope turns positive (rising 2 consecutive
  bars) with close above EMA(50); short on the mirror image; exit
  when the slope reverses — as specified. Entries fire once per slope
  streak (first bar of a 2-bar rise), not on every rising bar.
- 2xATR stop, 3xATR trail, 150-bar max hold; warmup 80 — as specified.
- Source URL taken verbatim from a browser search result (QuantVPS
  CVD guide), not guessed.
