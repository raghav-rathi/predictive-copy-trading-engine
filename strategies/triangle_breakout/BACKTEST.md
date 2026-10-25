# Triangle Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=100 bars.

## Results (shipped config: 5-bar zigzag, 1% flat-side tolerance,
breakout entry, reclaim exit, 2xATR stop, 2.5xATR trail, 96-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 44 | 25.0% | -$113 | -1.1% | -0.15 | -9.8% | -$2.57 | 0.93 |
| ETH | 20 | 45.0% | +$713 | +7.1% | +1.54 | -3.4% | +$35.67 | 2.45 |
| HYPE | 17 | 23.5% | +$305 | +3.1% | +0.85 | -5.9% | +$17.95 | 1.47 |
| **Combined** | **81** | — | **+$905** | — | — | — | +$11.17 | — |

Fees: BTC $509, ETH $172, HYPE $80 (total $761).
Exits: 44 stop / 37 signal — a balanced exit mix for a continuation
pattern; nearly half the trades reach their signal exit.

## Verdict: green but thin — the ETH leg is interesting, the sample
isn't

+$905 on 81 trades, with BTC essentially flat (-$113), ETH strong
(+$713, 45% win, PF 2.45 on 20 trades), and HYPE modest (+$305 on 17
trades). The ETH leg is the best-looking small sample in the batch,
but 20 trades cannot carry a verdict. The pattern's economics are
plausible (continuation breakouts after consolidation), and unlike
the reversal patterns it doesn't fight the trend — but plausibility
is not evidence. Needs a longer window or more coins before anyone
calls this an edge.

## Mechanism

5-bar zigzag pivots, 1% flat-side tolerance, breakout entry,
reclaim/opposite-triangle exit, 2xATR stop, 2.5xATR trail, 96-bar
max hold. All params fixed a priori; no optimization.

Source: ascending / descending triangles (Bulkowski, Encyclopedia
of Chart Patterns).

## Limitations

- 81 trades total; no leg exceeds 44 trades — do not quote any leg
  as an edge.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
