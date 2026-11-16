# Elliott Wave Count — Calibration

Pivot-size sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, wave-2
band 38.2–61.8%, 161.8% extension, 2xATR stop, 3xATR target, 96-bar
max hold). The sweep re-runs `add_indicators(df, pivot_n=N)` only —
signals and risk are unchanged.

| Pivot | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 3 | BTC | 28 | 17.9% | -$938 | -3.91 | 0.11 | -$33.50 |
| 3 | ETH | 10 | 40.0% | -$215 | -1.09 | 0.52 | -$21.52 |
| 3 | HYPE | 15 | 13.3% | -$212 | -1.00 | 0.51 | -$14.13 |
| 5 (shipped) | BTC | 20 | 35.0% | +$58 | +0.24 | 1.14 | +$2.90 |
| 5 (shipped) | ETH | 13 | 38.5% | -$160 | -0.69 | 0.70 | -$12.29 |
| 5 (shipped) | HYPE | 1 | 100.0% | +$58 | +0.93 | inf | +$57.76 |
| 7 | BTC | 23 | 39.1% | -$131 | -0.45 | 0.83 | -$5.71 |
| 7 | ETH | 19 | 36.8% | +$71 | +0.30 | 1.12 | +$3.75 |
| 7 | HYPE | 3 | 66.7% | -$6 | -0.05 | 0.85 | -$1.89 |

## One-line verdict

- **3:** clearly worse — combined -$1,365 on 53 trades, and every
  coin red. Finer pivots admit noisier counts: BTC win rate collapses
  to 17.9% with PF 0.11, i.e. the wave-3 breakouts it admits are
  mostly noise.
- **7:** combined -$66 on 45 trades — also ~breakeven noise, with the
  sign split across coins (ETH +$71, BTC -$131, HYPE -$6).
- **5 (shipped):** least bad combined (-$44 on 34 trades) — but with
  34 trades that ranking is itself noise; HYPE's 100% win rate is a
  single trade.
- **Shipped decision:** keep the specified 5-bar pivots regardless.
  The 5-bar size was fixed before any backtest was run; leaning
  toward 5 *because* it is least bad would still be in-sample
  selection on a window where no setting earns anything. The honest
  read: the pivot size changes how often the strict count fires, not
  whether it pays — on this window it does not pay at any size.
