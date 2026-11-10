# Clenow Trend Following — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 3xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 3 | 33.3% | 37.66 | 0.28 | -1.6% | 12.55 | 1.23 |
| ETH | 3 | 33.3% | -119.89 | -0.95 | -2.0% | -39.96 | 0.36 |
| HYPE | 11 | 9.1% | -561.58 | -2.32 | -5.6% | -51.05 | 0.08 |
| **Combined** | **17** | **17.6%** | **-643.81** | **-2.05** | **-2.6%** | **-37.87** | **0.33** |

Fees: total $80.99.
Exits: BTC {'stop': 3}; ETH {'stop': 3}; HYPE {'stop': 11}.
All 17 trades exited on the 3x ATR trailing stop; zero signal exits.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,356.19.

## Verdict: Loser combined on paper (−$643.81, PF 0.33, Sharpe −2.05).

This is a very slow system on 1h crypto — only 17 trades in ~8 months, and every single one died on the trailing stop. BTC eked out +$37.66 on 3 trades, but ETH (−$119.89) and especially HYPE (−$561.58, 1 win in 11) lost. The 50-day breakout entries arrive so late in the move that the 3x ATR stop is nearly always the exit, and the winners never run far enough to cover the losers: gross wins $316.18 vs gross losses $960.00. With n=17 the sample is far too small to condemn the system outright, but as shipped on this window it is a loser, and the HYPE leg (9.1% win rate) shows the 50-day breakout whipsaws badly on the most volatile coin. Not a tradeable signal as shipped.

## Limitations

- Only 17 trades: the per-coin numbers are statistically meaningless
  on their own; the verdict rests on the combined PF 0.33 and the
  uniform stop-exit pattern, not on any single coin.
- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The entry rule is the closest-faithful breakout variant documented
  in CALIBRATION.md (close vs the prior 1200-bar extreme), because the
  literal inclusive-window rule never fires on 1h data.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
