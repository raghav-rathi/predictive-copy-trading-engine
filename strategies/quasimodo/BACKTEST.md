# Quasimodo Reversal — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795010400000) (2026-03-14 22:00 UTC →
2026-11-18 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5968, ETH 5968, HYPE 5966.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 8 | 37.5% | -144.71 | -0.53 | -3.1% | -18.09 | 0.51 |
| ETH | 4 | 50.0% | 982.97 | 1.44 | -2.2% | 245.74 | 8.29 |
| HYPE | 10 | 50.0% | -265.19 | -0.91 | -5.2% | -26.52 | 0.45 |
| **Combined** | **22** | **45.5%** | **573.07** | **0.72** | **-2.5%** | **26.05** | **1.62** |

Fees: total $158.57.
Exits: BTC {'stop': 8}; ETH {'stop': 4}; HYPE {'stop': 10}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$30,573.07.

## Verdict: WINNER (nominal, thin sample) — +$573.07 on 22 trades, combined Sharpe 0.72, MaxDD -2.5%.

The combined row is green, but do not read an edge into it: the
entire profit comes from 4 ETH trades (+$982.97, PF 8.29,
expectancy +$245.74/trade — one or two large winners), while BTC
loses (-$144.71, PF 0.51) and HYPE loses (-$265.19, PF 0.45).
With 22 trades total, the combined +$573.07 is statistically
indistinguishable from luck, and two of three coins lose. The
exit split (22 stop vs 0 signal) shows the QM exits never fire —
every trade lives or dies on the 2xATR stop/trail. No parameter
was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Only 22 trades — the combined win rests on 4 ETH trades and is
  not a robust edge claim; BTC and HYPE both lose.
- The shoulder guards (must sit above the break low; retracement
  must cross the neckline) and the expiries are interpretation
  choices (see CALIBRATION.md); a looser reading trades more
  (mostly continuation) patterns.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
