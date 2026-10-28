# Rectangle Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), window 2026-03-14 →
2026-10-27, $10k start, 1% risk per trade on the 2xATR stop, 3x
leverage cap, 0.045% fee + 0.01% slippage per side, funding off.
WARMUP=30 bars. Bars: 5,443 per coin (filtered t >=
1773525600000).

## Results (shipped config: 20-bar range, width < 4%, held ≥ 15
bars, volume > 1.2x average, 2xATR stop, 2.5xATR trail, 168-bar
max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 112 | 33.0% | -$1,538 | -1.48 | -18.7% | -$13.73 | 0.70 |
| ETH | 76 | 39.5% | +$1,004 | +1.09 | -6.2% | +$13.21 | 1.28 |
| HYPE | 41 | 36.6% | -$731 | -1.24 | -8.4% | -$17.84 | 0.64 |
| **Combined** | **229** | **35.8%** | **-$1,266** | — | — | **-$5.53** | — |

Fees: BTC $1,271, ETH $768, HYPE $271 (total $2,310).
Exits: 223 stop / 6 signal — the signal exit almost never fires;
the stop does nearly all the work.

## Verdict: loser

-$1,266 across 229 trades is a clear loser, not noise: two of
three coins lose, win rate sits at 35.8%, and the profit factor
never clears 1.28 on any leg. ETH's green leg (+$1,004, PF 1.28)
is the only bright spot and is not large enough to carry the
book. The textbook rectangle breakout does not survive 1h crypto
in this window — breakouts here are more often traps than
continuation, and the trailing-window exit exits too early to
let winners run.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
