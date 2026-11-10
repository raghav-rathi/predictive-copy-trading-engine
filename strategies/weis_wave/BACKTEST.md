# Weis Wave — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first), filtered to
the window before indicators. $10k start per coin, 1% risk per trade
on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per
side, funding off.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 323 | 28.8% | -4354.18 | -3.63 | -45.8% | -13.48 | 0.64 |
| ETH | 332 | 35.2% | -2163.58 | -1.31 | -30.1% | -6.52 | 0.82 |
| HYPE | 272 | 34.9% | -2553.91 | -2.07 | -27.4% | -9.39 | 0.73 |
| **Combined** | **927** | **32.9%** | **-9071.67** | **-3.28** | **-32.5%** | **-9.79** | **0.73** |

Fees: total $6475.17.
Exits: BTC {'signal': 176, 'stop': 147}; ETH {'signal': 184, 'stop': 148}; HYPE {'signal': 144, 'stop': 128}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Loser combined on paper (−$9,071.67, PF 0.73, Sharpe −3.28).

The Weis Wave loses on every coin in this window, and badly: BTC
−$4,354.18 with a −45.8% drawdown, ETH −$2,163.58, HYPE −$2,553.91.
It fires 927 times in ~8 months — the 1.5xATR swing definition flips
waves constantly on 1h crypto, so the "drying volume into the turn"
filter is not selective enough to overcome the churn: 504 of 927
trades exit on the next wave flip (signal) and 423 die on the ATR
stop, with a 32.9% win rate and PF 0.73. The volume comparison is
also structurally weak here — a completed wave's volume is dominated
by how long the wave lasted, not by conviction, so "less volume than
the wave before" mostly just means "shorter wave". Not a tradeable
signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The reversal bar is assigned to the new wave (see CALIBRATION.md);
  the alternative assignment would shift completed-wave volumes by
  one bar's volume.
- ATR(14) is NaN for the first 13 bars, so no wave can flip before
  bar 14; WARMUP (60) covers this.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
