# Dow Theory Trend — Calibration

Pivot-size sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, 33–66%
pullback, volume filter, 2xATR stop, 4xATR target, 120-bar max hold).
The sweep re-runs `add_indicators(df, pivot_n=N)` only — signals and
risk are unchanged.

| Pivot | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 3 | BTC | 121 | 40.5% | -$115 | -0.05 | 0.98 | -$0.95 |
| 3 | ETH | 121 | 36.4% | +$859 | +0.85 | 1.17 | +$7.10 |
| 3 | HYPE | 116 | 37.1% | -$1,226 | -1.64 | 0.70 | -$10.57 |
| 5 (shipped) | BTC | 90 | 34.4% | -$917 | -1.06 | 0.80 | -$10.19 |
| 5 (shipped) | ETH | 87 | 31.0% | -$1,562 | -1.71 | 0.66 | -$17.95 |
| 5 (shipped) | HYPE | 85 | 40.0% | +$469 | +0.55 | 1.12 | +$5.52 |
| 7 | BTC | 74 | 39.2% | -$33 | +0.03 | 0.99 | -$0.45 |
| 7 | ETH | 73 | 27.4% | -$1,555 | -1.70 | 0.64 | -$21.30 |
| 7 | HYPE | 65 | 43.1% | +$437 | +0.56 | 1.14 | +$6.73 |

## One-line verdict

- **3:** the least bad combined (-$482) — but only because it rescues
  ETH (+$859) while destroying HYPE (-$1,226, Sharpe -1.64). Finer
  pivots fire 358 trades and still lose.
- **7:** combined -$1,151; BTC goes flat (-$33) and HYPE stays green
  (+$437), but ETH is still the hole (-$1,555, expectancy -$21.30).
- **5 (shipped):** worst combined (-$2,009) — the middle setting is
  the worst of the three, which says the pivot size is not the
  binding constraint: the entry logic itself loses.
- **Shipped decision:** keep the specified 5-bar pivots regardless.
  The 5-bar size was fixed before any backtest was run; the in-sample
  ranking does not change that, and leaning toward 3 *because* it
  is least bad would be in-sample selection on a window where no
  setting works on more than one coin. The honest read: the pivot
  size moves which coin pays, not whether the strategy works.
