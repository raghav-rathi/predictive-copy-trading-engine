# MACD Histogram Divergence — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=80 bars.

## Results (shipped config: MACD(12,26,9) histogram divergence on
5-bar zigzag pivots, zero-cross-after-confirmation exit, 2xATR
stop, 2.5xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 81 | 28.4% | -$1,729 | -17.3% | -2.20 | -26.7% | -$21.34 | 0.58 |
| ETH | 79 | 30.4% | -$97 | -1.0% | -0.05 | -14.2% | -$1.23 | 0.97 |
| HYPE | 84 | 42.9% | +$3,383 | +33.8% | +2.70 | -4.2% | +$40.27 | 1.91 |
| **Combined** | **244** | — | **+$1,557** | — | — | — | +$6.38 | — |

Fees: BTC $806, ETH $625, HYPE $458 (total $1,889).
Exits: 165 stop / 79 signal — the stop still dominates, but the
signal exit works often enough to matter (32% of trades).

## Verdict: the batch's best print — and still not an edge

+$1,557 combined is the batch's best result, carried entirely by
HYPE (+$3,383, 42.9% win, PF 1.91, Sharpe 2.70 on 84 trades — the
strongest single leg in the batch). BTC loses (-$1,729, PF 0.58) and
ETH is flat (-$97, PF 0.97). The honest read: one coin's divergence
signal works well, two coins' don't, and 84 trades on the green leg
is enough to be interesting but not enough to be a finding. The
divergence thesis survives this window better than any other thesis
in the batch — it deserves a longer window or more coins before
anyone calls it an edge, and it is the only batch-16 strategy worth
that follow-up.

## Mechanism

MACD(12,26,9) histogram divergence on 5-bar zigzag pivots, fire once
per pivot pair, zero-cross-after-confirmation exit, 2xATR stop,
2.5xATR trail, 120-bar max hold. All params fixed a priori; no
optimization.

Source: MACD-Histogram divergence (Appel; Aspray, StockCharts
ChartSchool).

## Limitations

- 244 trades total; the HYPE leg (84 trades) is interesting but
  not significant.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
