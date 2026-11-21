# Williams VIX Fix — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795269600000) (2026-03-14 22:00 UTC →
2026-11-21 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6040, ETH 6040, HYPE 6038.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 452 | 39.6% | -4506.01 | -2.97 | -49.5% | -9.97 | 0.72 |
| ETH | 430 | 44.2% | -1061.36 | -0.41 | -23.5% | -2.47 | 0.94 |
| HYPE | 431 | 42.5% | -2716.30 | -1.69 | -41.0% | -6.30 | 0.82 |
| **Combined** | **1313** | **42.0%** | **-8283.67** | **-2.22** | **-33.8%** | **-6.31** | **0.83** |

Fees: total $8074.14.
Exits: BTC {'stop': 290, 'signal': 162}; ETH {'stop': 261, 'signal': 169}; HYPE {'stop': 260, 'signal': 171}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$21,716.33.

## Verdict: LOSER — -$8,283.67 on 1313 trades, combined Sharpe -2.22, MaxDD -33.8%.

All three coins lose; BTC is the worst (-$4,506.01, PF 0.72, MaxDD
-49.5%). Gross PnL before fees is only about -$210 (net + fees), so
the entries are roughly breakeven before costs and the $8,074 of fees
turns the strategy into a large loser — the fear-spike entries carry
no edge on this window at 1h crypto frequency. Signal exits (502 of
1313) do fire often, so the opposite-flash exit is active, but it does
not save the trades. No parameter was tuned; the spec shipped as
written, and both calibration alternates lost more money (see
CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The range-high rule (0.85 x 50-bar max WVF) fires often in choppy
  regimes, so entries are frequent (~1 trade per 14 bars per coin)
  and fee-sensitive.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
