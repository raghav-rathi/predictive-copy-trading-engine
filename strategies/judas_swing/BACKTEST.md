# Judas Swing — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 48 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 32 | 37.5% | -644.36 | -1.09 | -9.9% | -20.14 | 0.60 |
| ETH | 38 | 28.9% | -854.99 | -1.43 | -15.7% | -22.50 | 0.59 |
| HYPE | 35 | 25.7% | -653.28 | -1.10 | -10.0% | -18.67 | 0.65 |
| **Combined** | **105** | **30.5%** | **-2152.63** | **-1.90** | **-10.6%** | **-20.50** | **0.61** |

Fees: total $853.96.
Exits: BTC {'stop': 30, 'max_hold': 1, 'signal': 1}; ETH {'stop': 30, 'signal': 5, 'max_hold': 3}; HYPE {'stop': 33, 'signal': 2}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,847.37.

## Verdict: LOSER — -$2,152.63 on 105 trades, combined Sharpe -1.90, MaxDD -10.6%.

All three coins lose with the same shape (win rate 26–38%, PF
0.59–0.65, expectancy about -$20/trade): the London-window sweep
does not reverse reliably in 24/7 crypto — the "fakeout" more often
continues than reverses, and 93 of 105 trades end on the 2xATR stop.
Fees ($853.96) are a large share of the loss but not the whole story;
gross of fees the strategy is still negative. No parameter was tuned;
the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The session times are a clock rule imposed on a 24/7 market (no
  real London open in crypto); the Asian range / London window
  boundaries are interpretation choices (see CALIBRATION.md).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
