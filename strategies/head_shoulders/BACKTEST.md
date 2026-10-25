# Head and Shoulders — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=100 bars.

## Results (shipped config: 5-bar zigzag, 3% shoulder tolerance,
conservative neckline, reclaim exit, 2xATR stop, 2.5xATR trail,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 31 | 29.0% | +$36 | +0.4% | +0.11 | -4.6% | +$1.15 | 1.04 |
| ETH | 23 | 34.8% | +$558 | +5.6% | +1.21 | -3.4% | +$24.28 | 1.97 |
| HYPE | 6 | 33.3% | -$136 | -1.4% | -0.65 | -3.2% | -$22.74 | 0.27 |
| **Combined** | **60** | — | **+$458** | — | — | — | +$7.63 | — |

Fees: BTC $323, ETH $164, HYPE $27 (total $514).
Exits: 35 stop / 25 signal — the most balanced exit mix in the
batch, which fits a reversal pattern: about half the trades reach
their signal exit instead of dying on the stop.

## Verdict: flat — the least-bad pattern in the batch, which is not
a recommendation

+$458 on 60 trades is flat, not green: BTC is +$36 (noise), ETH is
+$558 on 23 trades (PF 1.97, the best single leg among the pattern
strategies), HYPE is -$136 on 6 trades (noise). The honest read is
that H&S at 1h granularity is a coin flip with good trade
management — the exits work (42% signal exits), but the entries
don't separate from chance. A longer window or more coins might
separate ETH's leg from noise; this window cannot.

## Mechanism

5-bar zigzag pivots, 3% shoulder tolerance, conservative neckline,
reclaim/opposite-pattern exit, 2xATR stop, 2.5xATR trail, 120-bar
max hold. All params fixed a priori; no optimization.

Source: head and shoulders (Bulkowski, Encyclopedia of Chart
Patterns).

## Limitations

- 60 trades total; HYPE's 6 trades say nothing — do not quote any
  single leg as an edge.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
