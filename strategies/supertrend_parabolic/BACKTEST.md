# Supertrend Parabolic — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795010400000) (2026-03-14 22:00 UTC →
2026-11-18 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5968, ETH 5968, HYPE 5966.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 302 | 30.1% | -3153.90 | -2.06 | -41.7% | -10.44 | 0.75 |
| ETH | 295 | 34.6% | -1156.92 | -0.53 | -28.7% | -3.92 | 0.91 |
| HYPE | 340 | 35.0% | -1919.73 | -1.13 | -26.9% | -5.65 | 0.86 |
| **Combined** | **937** | **33.3%** | **-6230.56** | **-1.64** | **-27.5%** | **-6.65** | **0.84** |

Fees: total $6688.69.
Exits: BTC {'stop': 201, 'signal': 101}; ETH {'stop': 219, 'signal': 76}; HYPE {'stop': 198, 'signal': 142}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$23769.44.

## Verdict: LOSER — -$6,230.56 on 937 trades, combined Sharpe -1.64, MaxDD -27.5%.

Supertrend + PSAR agreement loses badly on 1h crypto: 937 trades,
a 33.3% win rate, PF 0.84, and -$6,230.56 net after $6,688.69 in
fees. No coin wins — BTC is the worst (-$3,153.90, Sharpe -2.06,
MaxDD -41.7%), HYPE loses -$1,919.73 and ETH -$1,156.92. The exit
split (618 stop vs 319 signal) shows the either-line-flip exit
fires often but does not save the trades: requiring both trend
tools to agree delays entries until the move is already extended,
and the trades then reverse into the 2xATR stop. Two lagging
trend tools agreeing is not a filter — it is a late-entry machine.
No parameter was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 937 trades is a large sample and the loss is present on all
  three coins — the edge is absent, not merely unlucky.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
