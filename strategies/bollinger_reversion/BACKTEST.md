# Bollinger Bands %b Mean Reversion — Backtest

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
| BTC | 376 | 41.2% | -6248.24 | -5.57 | -63.1% | -16.62 | 0.52 |
| ETH | 361 | 41.0% | -6480.11 | -5.31 | -65.8% | -17.95 | 0.52 |
| HYPE | 367 | 43.6% | -4283.20 | -3.40 | -46.8% | -11.67 | 0.69 |
| **Combined** | **1104** | **41.9%** | **-17011.55** | **-6.27** | **-57.4%** | **-15.41** | **0.58** |

Fees: total $5952.73.
Exits: BTC {'stop': 218, 'signal': 158}; ETH {'stop': 220, 'signal': 141}; HYPE {'stop': 198, 'signal': 169}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$12,988.45.

## Verdict: LOSER — -$17,011.55 on 1,104 trades, combined Sharpe -6.27, MaxDD -57.4%.

Mean reversion into the band tag fails decisively on 1h crypto in
this window: all three coins lose, profit factor 0.52–0.69, and
the combined book gives back 57% of equity. The exit (close back
to the middle band) is too slow — 636 of 1,104 trades end on the
harness stop rather than the signal exit, i.e. price keeps running
through the tag instead of reverting, and the 2xATR stop is what
cuts the trade. In a strongly trending window (BTC fell from
~$71k to the low-$60ks with sharp downdrafts) buying lower-band
tags is catching a falling knife. No parameter was tuned; the spec
shipped as written, and the alternates in CALIBRATION.md lose too.

## Limitations

- Single ~8-month crypto window, heavily trending down in its
  second half; funding unmodeled; next-bar-open execution vs
  idealized entry.
- 1,104 trades is a large sample and the three coins agree in
  sign — this is a robust loser, not a borderline one.
- The tag rule uses the close vs the band (not the wick), and the
  exit is the middle band, per the spec; see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
