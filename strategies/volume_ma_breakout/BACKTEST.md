# Volume MA Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794924000000) (2026-03-14 22:00 UTC →
2026-11-17 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5944, ETH 5944, HYPE 5942.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 285 | 30.5% | -3020.81 | -1.81 | -37.9% | -10.60 | 0.77 |
| ETH | 278 | 34.2% | -1719.82 | -0.86 | -32.8% | -6.19 | 0.86 |
| HYPE | 261 | 32.6% | -1180.98 | -0.57 | -26.6% | -4.52 | 0.91 |
| **Combined** | **824** | **32.4%** | **-5921.62** | **-1.45** | **-25.7%** | **-7.19** | **0.84** |

Fees: total $6139.92.
Exits: BTC {'stop': 252, 'signal': 33}; ETH {'stop': 250, 'signal': 28}; HYPE {'stop': 228, 'signal': 33}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,078.38.

## Verdict: LOSER — -$5,921.62 on 824 trades, combined Sharpe -1.45, MaxDD -25.7%.

Volume-confirmed 20-bar breakouts lose on every coin on this
window: BTC -$3,020.81 (PF 0.77, Sharpe -1.81, MaxDD -37.9%),
ETH -$1,719.82 (PF 0.86), HYPE -$1,180.98 (PF 0.91). Win rates
sit at 30–34% with expectancy -$4.52 to -$10.60 per trade, and
fees alone ($6,139.92) exceed the combined loss — the system
trades 824 times and pays more in fees than it loses net of
them, which says the entries carry no edge after costs. The
exit split is damning for the spec's exit: only 94 of 824
trades ended on the 10-bar-range signal and 730 on the harness
stop/trail, so the shipped system is effectively a breakout
entry plus the 2xATR stop / 2.5xATR trail — and on 1h crypto
that combination buys the top of the spike and stops out.
The 1.5x volume filter does not save it: a volume spike at a
fresh 20-bar high on 1h bars is more often exhaustion or a
liquidity grab than the start of a run.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 824-trade sample, and the loss is broad-based (all three coins
  negative, PF 0.77–0.91) — the edge is absent, not one-coin driven.
- The 10-bar-range exit almost never fires (94/824); the
  reported result is really the entry + harness stop/trail, not
  the full breakout system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
