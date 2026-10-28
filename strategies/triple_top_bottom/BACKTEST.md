# Triple Top / Bottom — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), window 2026-03-14 →
2026-10-27, $10k start, 1% risk per trade on the 2xATR stop, 3x
leverage cap, 0.045% fee + 0.01% slippage per side, funding off.
WARMUP=70 bars. Bars: 5,443 per coin (filtered t >=
1773525600000).

## Results (shipped config: 2-bar-lagged pivots, three pivots
within 1.5%, ≥ 5 bars apart, ≤ 60-bar span, neckline-close
confirmation, 2xATR stop, 2.5xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 59 | 35.6% | -$127 | -0.08 | -11.9% | -$2.15 | 0.96 |
| ETH | 47 | 25.5% | -$551 | -0.62 | -17.7% | -$11.71 | 0.79 |
| HYPE | 24 | 45.8% | -$329 | -0.71 | -5.9% | -$13.69 | 0.68 |
| **Combined** | **130** | **33.8%** | **-$1,006** | — | — | **-$7.74** | — |

Fees: BTC $729, ETH $452, HYPE $134 (total $1,315).
Exits: 125 stop / 5 signal — opposite patterns almost never
arrive while a trade is open; the stop exits nearly everything.

## Verdict: loser

-$1,006 across 130 trades, losing on every coin, win rate
33.8%, no leg above PF 0.96. BTC is nearly flat (-$127) but
that is the best leg on offer, which says everything. Triple
tops/bottoms as mechanically defined here carry no edge on 1h
crypto in this window.

## Limitations

- Only 130 trades; the pattern is rare, so the estimate is
  noisy — but the sign is negative on all three coins, which
  argues against "just noise".
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
