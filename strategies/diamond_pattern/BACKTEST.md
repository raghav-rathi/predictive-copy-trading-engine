# Diamond Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), window 2026-03-14 →
2026-10-27, $10k start, 1% risk per trade on the 2xATR stop, 3x
leverage cap, 0.045% fee + 0.01% slippage per side, funding off.
WARMUP=50 bars. Bars: 5,443 per coin (filtered t >=
1773525600000).

## Results (shipped config: 15–40 bar pattern, apex range >
1.3x start range, end range < 0.7x apex range, volume > 1.2x
pattern average, 2xATR stop, 2.5xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 35 | 42.9% | -$150 | -0.20 | -9.5% | -$4.27 | 0.91 |
| ETH | 35 | 45.7% | +$934 | +1.39 | -9.6% | +$26.70 | 1.57 |
| HYPE | 27 | 14.8% | -$1,161 | -2.71 | -13.9% | -$43.00 | 0.25 |
| **Combined** | **97** | **36.1%** | **-$376** | — | — | **-$3.88** | — |

Fees: BTC $404, ETH $329, HYPE $128 (total $861).
Exits: 95 stop / 2 signal.

## Verdict: loser (small, and split)

-$376 across 97 trades is the batch's smallest loss, but it is
still a loss, and the split is damning: ETH's +$934 (PF 1.57)
against HYPE's -$1,161 (PF 0.25, 14.8% win rate) means the
pattern has no consistent behavior across coins. With only 97
trades, the honest read is "no edge demonstrated", not "nearly
profitable".

## Limitations

- Only 97 trades; the estimate is noisy and coin-dependent.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
