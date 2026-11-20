# Prior-Week Range Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795183200000) (2026-03-14 22:00 UTC →
2026-11-20 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6016, ETH 6016, HYPE 6014. (HYPE's cache
starts 2 bars into the window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 221 | 16.7% | -5338.21 | -5.05 | -55.4% | -24.15 | 0.40 |
| ETH | 213 | 16.9% | -5357.54 | -4.77 | -55.2% | -25.15 | 0.42 |
| HYPE | 270 | 20.7% | -5335.83 | -4.21 | -54.3% | -19.76 | 0.47 |
| **Combined** | **704** | **18.3%** | **-16031.58** | **-6.28** | **-54.5%** | **-22.77** | **0.43** |

Fees: total $3346.22.
Exits: BTC {'stop': 142, 'signal': 79}; ETH {'stop': 142, 'signal': 71}; HYPE {'stop': 171, 'signal': 99}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$13,965.85.

## Verdict: LOSER — -$16,031.58 on 704 trades, combined Sharpe -6.28, MaxDD -54.5%.

Buying the prior week's high and shorting its low on 1h crypto
fails badly: win rate 17–21%, profit factor 0.40–0.47, and every
coin loses more than half its starting equity. Breakouts of a
weekly range on hourly bars are mostly false breakouts in this
window — price pokes through the level and comes straight back,
and the exit (close back inside the range) plus the 2xATR stop
cut the trade for a loss either way: 455 of 704 trades end on
the stop, 249 on the signal exit. Note the near-identical
per-coin losses (-$5,338 / -$5,358 / -$5,336): the three books
are different trades, but the same stop structure on the same
regime produces the same damage. No parameter was tuned; the
spec shipped as written, and the alternates in CALIBRATION.md
lose too.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 704 trades is a large sample and the three coins agree in sign
  and magnitude — this is a robust loser, not a borderline one.
- The level uses the week's high/low wicks, and the entry uses
  the close vs the level; see CALIBRATION.md for the
  closes-only alternate.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
