# Value-Area Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990. (The CSVs each
contain one further bar at exactly END_MS; the half-open window
excludes it, which is why the counts are one below the 5993/5991
figures in the batch brief. HYPE's cache starts 2 bars into the
window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 325 | 26.2% | -2776.72 | -2.00 | -31.5% | -8.54 | 0.73 |
| ETH | 305 | 27.5% | -2088.17 | -1.41 | -22.2% | -6.85 | 0.80 |
| HYPE | 317 | 28.1% | -1421.52 | -0.95 | -15.6% | -4.48 | 0.86 |
| **Combined** | **947** | **27.2%** | **-6286.41** | **-2.03** | **-21.4%** | **-6.64** | **0.80** |

Fees: total $6674.62.
Exits: BTC {'signal': 181, 'stop': 144}; ETH {'signal': 161, 'stop': 144}; HYPE {'signal': 180, 'stop': 137}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$23,727.16.

## Verdict: LOSER — -$6,286.41 on 947 trades, combined Sharpe -2.03, MaxDD -21.4%.

All three coins lose with the same shape: ~27% win rate, profit
factor 0.73–0.86, expectancy -$4.48 to -$8.54 per trade. The
two-close acceptance rule fires constantly (947 trades in ~8
months — roughly 4 a day across the three coins) and the
rejection exit cuts most of them quickly, so the strategy is
mostly paying the 0.055%-per-side round-trip cost to fade noise
around a daily level: total fees $6,674.62 exceed the combined net
loss, i.e. gross of fees the strategy is roughly flat-to-slightly
negative and fees do the rest. Nothing here suggests an edge; the
value area built from a single prior day is too noisy a level on
1h crypto. No parameter was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The first profile comes from a 2-bar partial day (window starts
  22:00 UTC); see CALIBRATION.md.
- 947 trades is a large sample for a loser verdict, but it is still
  one window and three correlated coins — the loss is consistent,
  not a small-sample fluke.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
