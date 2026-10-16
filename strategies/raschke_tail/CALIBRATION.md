# raschke_tail — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two parameters: wick
strictness {2.0, 2.5x body} × entry window {3, 4 bars}. Runner:
`/tmp/batch7_run.py` (results in `/tmp/batch7_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (wick 2.0, win 3) | BTC | 134 | −$1,814 | −1.67 |
| shipped (wick 2.0, win 3) | ETH | 125 | −$592 | −0.36 |
| shipped (wick 2.0, win 3) | HYPE | 110 | −$591 | −0.43 |
| wick 2.0, win 4 | BTC | 146 | −$2,565 | −2.35 |
| wick 2.0, win 4 | ETH | 133 | −$924 | −0.62 |
| wick 2.0, win 4 | HYPE | 116 | −$1,268 | −1.05 |
| wick 2.5, win 3 | BTC | 115 | −$1,159 | −1.12 |
| wick 2.5, win 3 | ETH | 115 | −$75 | +0.05 |
| wick 2.5, win 3 | HYPE | 99 | −$142 | −0.03 |
| wick 2.5, win 4 | BTC | 125 | −$1,895 | −1.84 |
| wick 2.5, win 4 | ETH | 123 | −$425 | −0.23 |
| wick 2.5, win 4 | HYPE | 105 | −$852 | −0.68 |

## One-line verdicts

- **Stricter wick (2.5x) helps everywhere but fixes nothing:** combined
  loss shrinks from −$2,997 to −$1,376 and ETH/HYPE go near-flat — the
  marginal tails were pure noise. BTC still bleeds −$1,159.
- **A 4-bar window is strictly worse** on every coin and every wick
  setting: stale triggers fill on exhausted moves.
- **Verdict:** no variant turns a coin positive. The pattern's premise
  (exhaustion wick at a fresh extreme) misfires on hourly crypto, where
  extremes keep extending. Shipped config (wick 2.0, window 3) stands
  as the documented baseline; nothing promoted.
