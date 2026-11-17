# Triple RSI — Backtest

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
| BTC | 436 | 25.2% | -5128.40 | -3.74 | -55.1% | -11.76 | 0.63 |
| ETH | 426 | 27.9% | -3373.81 | -1.96 | -39.1% | -7.92 | 0.76 |
| HYPE | 432 | 28.7% | -2962.74 | -1.83 | -30.2% | -6.86 | 0.79 |
| **Combined** | **1294** | **27.3%** | **-11464.95** | **-3.28** | **-40.4%** | **-8.86** | **0.73** |

Fees: total $8120.59.
Exits: BTC {'stop': 219, 'signal': 217}; ETH {'stop': 225, 'signal': 201}; HYPE {'signal': 245, 'stop': 187}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$18544.82.

## Verdict: LOSER — -$11,464.95 on 1294 trades, combined Sharpe -3.28, MaxDD -40.4%.

The worst strategy of the batch by a wide margin. It loses on all
three coins (PF 0.63–0.79, win rates 25–29%, expectancy -$7 to
-$12 per trade), with BTC down -55.1% peak-to-trough and a
combined MaxDD of -40.4% on the $30k curve. The mechanism is
chasing, not confirming: requiring all three RSIs above 55 means
the entry fires only after a strong move is already well under
way — the fast RSI(7) leads, RSI(21) trails, and by the time the
slowest crosses 55 the move is exhausted and the trade buys the
top (or sells the bottom). The exit then fires at the first sign
of cooling — any RSI crossing 50 — so winners are cut short
while the 2xATR stop takes the losers (631 of 1294 exits are
stops, 663 are signal exits). 1294 trades at $8,120.59 in fees
compounds the damage. No parameter was tuned; the spec is shipped
as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1294-trade sample; the loss is consistent across all three
  coins, so it is a property of the entry/exit asymmetry, not
  one bad coin.
- The 55/45 entry vs 50 exit asymmetry means entries demand full
  agreement while exits need only one dissenter — the system is
  structurally slow in and fast out.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
