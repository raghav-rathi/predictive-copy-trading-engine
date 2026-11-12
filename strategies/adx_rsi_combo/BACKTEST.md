# ADX + RSI Combo — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 108 | 45.4% | -414.27 | -0.37 | -14.3% | -3.84 | 0.91 |
| ETH | 100 | 50.0% | 437.54 | 0.50 | -12.9% | 4.38 | 1.09 |
| HYPE | 100 | 33.0% | -1889.77 | -2.17 | -23.7% | -18.90 | 0.63 |
| **Combined** | **308** | **42.9%** | **-1866.50** | **-0.86** | **-14.2%** | **-6.06** | **0.87** |

Fees: total $2184.77.
Exits: BTC {'stop': 71, 'signal': 37}; ETH {'stop': 66, 'signal': 34}; HYPE {'stop': 80, 'signal': 20}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,133.50.

## Verdict: LOSER — -$1,866.50 on 308 trades, combined Sharpe -0.86, MaxDD -14.2%.

The ADX filter does not save the RSI mean-reversion entry on 1h
crypto. ETH is the only coin that clears breakeven (+$437.54, PF
1.09) and BTC is near-flat (-$414.27), but HYPE loses -$1,889.77
with a 33.0% win rate and Sharpe -2.17 — the RSI-30/70 crosses fire
into HYPE's sharp reversals and the 2xATR stop eats the trade before
the 50-midline exit can help. The exit split is healthier than most
batch systems (91 of 308 trades end on the RSI-50 signal exit rather
than the stop), so the exit logic does real work; the entry is the
problem. Win rate 42.9% with PF 0.87 means losers outrun winners
after $2,184.77 in fees.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 308-trade sample: a real sample, but one window and one coin
  (HYPE) driving the loss — the edge is not universal across coins.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
