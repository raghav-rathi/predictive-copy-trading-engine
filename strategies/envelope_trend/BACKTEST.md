# MA Envelope Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=30 bars.

## Results (shipped config: SMA(20) +/- 5% breakout, midline exit,
2xATR stop, 2.5xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 3 | 33.3% | +$301 | +3.0% | +1.36 | -1.7% | +$100.27 | 2.41 |
| ETH | 12 | 25.0% | +$14 | +0.1% | +0.07 | -4.1% | +$1.20 | 1.02 |
| HYPE | 33 | 36.4% | +$1,209 | +12.1% | +1.54 | -3.6% | +$36.62 | 1.93 |
| **Combined** | **48** | — | **+$1,524** | — | — | — | +$31.75 | — |

Fees: BTC $16, ETH $57, HYPE $110 (total $183).
Exits: 39 stop / 9 signal — the stop still dominates, but with only
48 trades the exit mix means little.

## Verdict: green but thin — rarity bought a positive print, not proof

+$1,524 combined is the batch's second-best print, and the thesis
(rarity buys quality) has something to it: the per-trade expectancy
(+$31.75) is the batch's best by an order of magnitude, and HYPE's
leg (+$1,209, PF 1.93, 33 trades) is genuinely decent. But 48 trades
across three coins in seven months — 3 on BTC — is far too thin to
call an edge. The BTC leg (+$301 on 3 trades) is a coin flip, and
the ETH leg (+$14) is flat. Treat this as a candidate for a longer
window or more coins, not a finding.

## Mechanism

SMA(20) +/- 5% breakout, midline exit, 2xATR stop, 2.5xATR
chandelier trail, 120-bar max hold. All params fixed a priori; no
optimization.

Source: moving-average envelopes (Murphy, Technical Analysis of the
Financial Markets).

## Limitations

- 48 trades total: no per-coin or combined statistic here is
  significant; do not quote the HYPE leg as an edge.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
