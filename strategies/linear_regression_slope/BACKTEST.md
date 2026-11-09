# Linear Regression Slope — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794232800000) (2026-03-14 22:00 UTC →
2026-11-09 14:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5752, ETH 5752, HYPE 5750.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 0 | — | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| ETH | 0 | — | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| HYPE | 0 | — | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| **Combined** | **0** | **—** | **0.00** | **0.00** | **0.0%** | **0.00** | **0.00** |

Fees: total $0.00.
Exits: {}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## Verdict: Untestable — zero trades on all three coins, so there is no result to judge.

This is structural, not a data or code fault (the slope was verified
bar-by-bar against `numpy.polyfit`). The entry demands R² ≥ 0.5 on
the exact bar the 20-bar slope flips sign — but at a turn the window
straddles the reversal, so the fit is poor by construction: on BTC
there are 155 positive slope turns and 156 negative ones, yet the
highest R² at any turn bar is 0.265 (mean 0.029), while R² ≥ 0.5
occurs 42% of the time overall. A clean trend only earns a high R²
after the turn is already old, and by then the slope has long since
turned. As briefed, the rule can essentially never fire. Zero trades
is not a winner, not a loser — it is untestable.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
