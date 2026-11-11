# Donchian ADX — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794402000000) (2026-03-14 22:00 UTC →
2026-11-11 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5776, ETH 5776, HYPE 5774.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 116 | 31.9% | -1369.62 | -1.14 | -20.5% | -11.81 | 0.73 |
| ETH | 111 | 34.2% | -299.42 | -0.15 | -18.5% | -2.70 | 0.94 |
| HYPE | 113 | 35.4% | 16.21 | 0.10 | -12.1% | 0.14 | 1.00 |
| **Combined** | **340** | **33.8%** | **-1652.84** | **-0.59** | **-10.6%** | **-4.86** | **0.90** |

Fees: total $2491.66.
Exits: BTC {'stop': 105, 'signal': 11}; ETH {'stop': 100, 'signal': 11}; HYPE {'stop': 106, 'signal': 7}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,347.16.

## Verdict: LOSER — -$1,652.84 on 340 trades, combined profit factor 0.90.

The ADX filter cut the trade count hard (340 trades vs the plain
Donchian breakout's much higher pace) but did not fix the underlying
problem: 20-bar breakouts on 1h crypto mostly fail. The exit split
says it plainly — 311 of 340 trades ended on the ATR stop and only 29
on the signal exit, so positions almost never survive long enough for
the ADX-decay exit to matter; the breakout reverses into the stop
first. HYPE's +$16.21 is a rounding error, not a win, and ETH's
-$299.42 with Sharpe -0.15 is flat-to-negative. ADX > 25 confirms a
trend was in force at entry, but on hourly bars that trend is usually
already exhausted by the time price prints a fresh 20-bar extreme —
the filter selects late entries, not good ones.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 340-trade sample: the loss is modest and fee-sized ($2,491.66 in
  fees vs -$1,652.84 net), so the verdict is a loser, but a
  close-to-breakeven one — the filter helps versus unfiltered
  Donchian, just not enough.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
