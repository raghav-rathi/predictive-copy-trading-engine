# Williams Accumulation/Distribution — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). One parameter varied
against the shipped config: the WAD smoothing window (shipped 20 →
10 / 40). Price SMA 50, 2xATR stop, 60-bar max hold unchanged.

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| WAD SMA 20 (shipped) | BTC | 393 | 19.3% | -$4,359 | -2.96 | 0.60 |
| WAD SMA 20 (shipped) | ETH | 386 | 16.8% | -$3,512 | -2.05 | 0.71 |
| WAD SMA 20 (shipped) | HYPE | 354 | 23.2% | -$2,490 | -2.04 | 0.75 |
| WAD SMA 10 | BTC | 598 | 20.9% | -$6,392 | -6.02 | 0.51 |
| WAD SMA 10 | ETH | 562 | 20.6% | -$5,334 | -3.93 | 0.59 |
| WAD SMA 10 | HYPE | 543 | 26.9% | -$3,577 | -3.01 | 0.74 |
| WAD SMA 40 | BTC | 324 | 16.7% | -$2,130 | -1.04 | 0.80 |
| WAD SMA 40 | ETH | 305 | 15.1% | -$3,695 | -2.26 | 0.63 |
| WAD SMA 40 | HYPE | 266 | 23.3% | +$106 | +0.20 | 1.01 |

## One-line verdict

- **WAD SMA 10:** faster signal, more trades (598 BTC), uniformly worse —
  the cross fires on noise and fees compound ($4,060 BTC alone).
- **WAD SMA 40:** fewer, later trades; cuts the BTC loss roughly in
  half and flips HYPE to a marginal +$106 (PF 1.01, Sharpe +0.20 —
  noise, not an edge), but ETH gets worse. No consistent improvement.
- **Shipped decision:** keep the specified WAD SMA 20 anyway. Nothing
  in the sweep shows a robust edge — the SMA-40 HYPE print is a
  single-coin, in-sample wobble (one cell of nine), not a reason to
  respec the strategy.
