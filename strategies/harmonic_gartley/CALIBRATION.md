# Harmonic Gartley — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). One variant against the
shipped config: relaxed ratio tolerance (±10% instead of ±6% on the
AB/XA and AD/XA point ratios) — same 5-bar zigzag, same textbook BC/CD
ranges, same 2xATR stop / 4xATR target / 100-bar max hold. Sweep script:
`/tmp/bt_new3.py` (`cal` mode).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped ±6% | BTC | 1 | 0.0% | -$112 | -1.91 | 0.00 |
| shipped ±6% | ETH | 0 | — | $0 | +0.00 | 0.00 |
| shipped ±6% | HYPE | 1 | 0.0% | -$105 | -2.01 | 0.00 |
| ±10% | BTC | 2 | 0.0% | -$220 | -1.94 | 0.00 |
| ±10% | ETH | 2 | 50.0% | +$79 | +0.65 | 1.70 |
| ±10% | HYPE | 4 | 50.0% | +$87 | +0.43 | 1.42 |

## One-line verdict

- **±10% tolerance:** finds 8 patterns instead of 2 (combined −$55 vs
  −$216), but 8 trades is still far too few to validate anything — the
  win rate and profit factors are lottery numbers. Relaxing the
  tolerance quadruples the sample without making it meaningful, and the
  looser pattern is arguably no longer the classical Gartley the
  strategy claims to test.
- **Shipped decision:** keep the specified ±6% classical tolerance as
  the registry config. The sweep's real finding is that the binding
  constraint is pattern rarity, not tolerance tuning: even at ±10%,
  ~1,560 zigzag pivots yield only 8 textbook patterns in 7 months of 1h
  crypto. Any "better" parameter would be in-sample selection on a
  single-digit trade count.
