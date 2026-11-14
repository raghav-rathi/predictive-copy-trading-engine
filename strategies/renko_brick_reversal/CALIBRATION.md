# Renko Brick Reversal — Calibration

Brick-size sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-18, same
costs/sizing, 2xATR stop, 3xATR trail, 200-bar max hold). The sweep
re-runs `renko_bricks(close, brick)` with the brick scaled to 0.5x /
1.0x / 1.5x the shipped ATR(14) mean — signals and risk unchanged.

| Brick size | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| 0.5x ATR | BTC | 148 | 33.8% | -$2,172 | -1.88 | 0.71 |
| 0.5x ATR | ETH | 137 | 33.6% | -$206 | -0.07 | 0.97 |
| 0.5x ATR | HYPE | 305 | 40.3% | +$1,835 | +1.16 | 1.14 |
| 0.5x ATR | **Combined** | **590** | — | **-$542** | — | — |
| 1.0x ATR (shipped) | BTC | 60 | 20.0% | -$2,139 | -3.00 | 0.42 |
| 1.0x ATR (shipped) | ETH | 54 | 27.8% | -$1,449 | -1.99 | 0.54 |
| 1.0x ATR (shipped) | HYPE | 131 | 30.5% | -$982 | -0.81 | 0.85 |
| 1.0x ATR (shipped) | **Combined** | **245** | — | **-$4,571** | — | — |
| 1.5x ATR | BTC | 22 | 9.1% | -$1,624 | -4.47 | 0.02 |
| 1.5x ATR | ETH | 23 | 4.3% | -$1,161 | -2.65 | 0.21 |
| 1.5x ATR | HYPE | 79 | 32.9% | -$339 | -0.27 | 0.92 |
| 1.5x ATR | **Combined** | **124** | — | **-$3,123** | — | — |

## One-line verdict

- **0.5x ATR:** far less bad combined (-$542) and the only setting
  with a green coin (HYPE +$1,835, Sharpe +1.16) — smaller bricks
  print sooner, so the reversal entry is less late and the 2xATR
  stop has more room relative to the brick. Still negative
  combined, and still a loser on BTC/ETH.
- **1.5x ATR:** the worst setting on BTC/ETH (win rates 9.1% /
  4.3% — the reversal is so late the trade is nearly always
  underwater immediately) and negative combined (-$3,123).
- **1.0x ATR:** the shipped a-priori default, negative everywhere
  (-$4,571 combined).
- **Shipped decision:** keep the specified 1.0x ATR brick size
  regardless. The 0.5x setting looks better only in-sample on this
  one 7-month window, and switching to it *because* it rescues the
  ledger would be in-sample selection. The honest read: brick size
  moves how late the entry is, not whether the reversal works —
  that still needs walk-forward or out-of-sample evidence, and on
  this window no brick size makes the strategy a winner.
