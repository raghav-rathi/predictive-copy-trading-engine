# Murrey Math Octave Reversal — Calibration

Frame-length sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-19, same costs/sizing, 2xATR stop,
80-bar max hold). The 64-bar frame is the specified Murrey octave
default; 32 and 128 test whether the edge is an artifact of the window
length.

| Frame | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| 64 (shipped) | BTC | 172 | 43.0% | -$2,206 | -1.86 | 0.78 |
| 64 (shipped) | ETH | 165 | 47.9% | -$376 | -0.19 | 0.96 |
| 64 (shipped) | HYPE | 195 | 43.6% | -$1,747 | -1.43 | 0.83 |
| 32 | BTC | 256 | 50.0% | -$3,517 | -3.15 | 0.69 |
| 32 | ETH | 251 | 49.0% | -$3,202 | -2.73 | 0.73 |
| 32 | HYPE | 297 | 49.5% | -$3,562 | -3.17 | 0.72 |
| 128 | BTC | 119 | 37.0% | -$1,518 | -1.33 | 0.81 |
| 128 | ETH | 111 | 44.1% | +$1,131 | +1.02 | 1.16 |
| 128 | HYPE | 136 | 27.9% | -$3,209 | -2.98 | 0.61 |

## One-line verdict

- **32-bar frame:** worse everywhere — more trades (whipsaw), deeper
  losses (-$3.2k to -$3.6k per coin). A shorter frame re-anchors faster,
  which is exactly the wrong thing in a trending window.
- **128-bar frame:** coin-dependent. BTC's loss shrinks (-$1,518 vs
  -$2,206), ETH flips positive (+$1,131, Sharpe +1.02, PF 1.16), but
  HYPE's loss nearly doubles (-$3,209, win% collapses to 27.9%). The
  longer frame helps the majors and hurts HYPE — not a robust
  improvement, and it cuts the sample to ~120 trades/coin.
- **Shipped decision:** keep the specified 64-bar frame. The 128-bar
  ETH result is a single-coin, in-sample bright spot inside an otherwise
  losing strategy; adopting it would be selecting on noise. If the
  strategy is ever revisited, the 128-bar frame on the majors is the
  thread to pull — with out-of-sample or walk-forward evidence, not
  this window.
