# Ehlers Instantaneous Trendline — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 853 | 21.7% | -7796.51 | -6.91 | -79.4% | -9.14 | 0.55 |
| ETH | 907 | 22.2% | -6809.19 | -4.93 | -72.4% | -7.51 | 0.63 |
| HYPE | 927 | 23.5% | -5053.87 | -3.40 | -50.8% | -5.45 | 0.77 |
| **Combined** | **2687** | **22.5%** | **-19659.57** | **-6.54** | **-66.8%** | **-7.32** | **0.66** |

Fees: total $12789.28.
Exits: BTC {'signal': 548, 'stop': 305}; ETH {'signal': 615, 'stop': 292}; HYPE {'signal': 674, 'stop': 253}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$10,397.40 (vs $30,000 + net −$19,659.57 = $10,340.43; the $56.97 gap
is the mark-to-market of positions still open at the window end).

## Verdict: LOSER — −$19,659.57 on 2,687 trades, combined Sharpe −6.54, MaxDD −66.8%.

The worst result of the batch by a wide margin, and the worst
single-strategy result in recent batches. The Instantaneous
Trendline's near-zero lag is exactly the problem on 1h crypto: the
line hugs price so closely that every hourly wiggle becomes a cross,
so the system flips direction 2,687 times in ~8 months (roughly one
trade every 6–7 bars per coin) with a 22.5% win rate and PF 0.66.
1,837 of the 2,687 trades ended on the opposite cross — the signal
exit is the dominant exit, not the stop — which means the system is
churning on its own signal: enter long on a cross up, get crossed
out (at a loss) a few bars later, reverse short, repeat. BTC lost
79.4% peak-to-trough and ended the window at a fraction of its
starting equity. Fees alone were $12,789.28. Ehlers designed the
trendline for daily bars with a trigger line and a cycle filter
around it; the bare close/trendline cross on hourly bars is a
whipsaw machine. This one is not salvageable by parameter tweaks —
the mechanism itself (zero-lag tracking) is the wrong tool for 1h
noise, and the spec forbids PnL tuning anyway.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 2,687-trade sample: the largest in the batch, and the loss is
  consistent across all three coins (PF 0.55–0.77) — this is a
  mechanism failure, not a one-coin artifact.
- The trigger-line variant (2·IT_t − IT_{t−2}) and the full adaptive
  Hilbert version were not tested; either might behave differently,
  but neither is the spec.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
