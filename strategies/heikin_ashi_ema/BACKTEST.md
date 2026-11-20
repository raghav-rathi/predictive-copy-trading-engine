# Heikin Ashi EMA — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795183200000) (2026-03-14 22:00 UTC →
2026-11-20 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6016, ETH 6016, HYPE 6014.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 977 | 20.4% | -9068.37 | -10.39 | -90.9% | -9.28 | 0.41 |
| ETH | 1020 | 23.1% | -8471.61 | -7.86 | -84.9% | -8.31 | 0.48 |
| HYPE | 898 | 29.8% | -6747.28 | -5.45 | -67.6% | -7.51 | 0.62 |
| **Combined** | **2895** | **24.3%** | **-24287.26** | **-9.82** | **-81.0%** | **-8.39** | **0.51** |

Fees: total $10697.88.
Exits: BTC {'signal': 694, 'stop': 283}; ETH {'signal': 748, 'stop': 272}; HYPE {'signal': 711, 'stop': 187}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$5,731.25.

## Verdict: LOSER (heavy) — -$24,287.26 on 2,895 trades, combined Sharpe -9.82, MaxDD -81.0%.

All three coins lose badly (PF 0.41 / 0.48 / 0.62, win rates
20–30%). The entry is a *state* condition, not a transition: as
long as the HA candle is bullish and the EMAs align, every bar
signals long, so the strategy re-enters immediately after every
signal exit and churns ~1 trade per 6 bars per coin. Heikin Ashi
candles flip direction constantly on 1h crypto, so the exit (HA
flip) fires almost immediately after entry — 2,153 of 2,895 trades
end on a signal exit, typically for a small loss plus fees. Fees
alone ($10,697.88) are ~44% of the loss; the rest is negative
expectancy per trade (-$8.39). No parameter was tuned; the spec
shipped as written, and both calibration alternates lose nearly
as much (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 2,895 trades is a very large sample and all three coins agree —
  this is a structural failure of the entry/exit pairing on 1h
  crypto, not noise.
- The state-based (non-transition) entry is the spec as written;
  a transition-only entry (e.g. HA flip bar only) would be a
  different strategy and was not tested.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
