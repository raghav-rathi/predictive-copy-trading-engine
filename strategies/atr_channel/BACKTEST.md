# ATR Channel Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=30 bars.

## Results (shipped config: SMA(20) +/- 1.5xATR(14) breakout, midline
exit, 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 215 | 32.1% | -$2,525 | -25.3% | -1.72 | -30.7% | -$11.74 | 0.74 |
| ETH | 216 | 33.3% | -$1,257 | -12.6% | -0.71 | -23.9% | -$5.82 | 0.87 |
| HYPE | 208 | 36.1% | +$1,943 | +19.4% | +1.23 | -12.8% | +$9.34 | 1.18 |
| **Combined** | **639** | — | **-$1,839** | — | — | — | -$2.88 | — |

Fees: BTC $2,095, ETH $1,627, HYPE $1,175 (total $4,897).
Exits: 417 stop / 222 signal — the midline exit does real work here
(35% of trades), unlike the crossover strategies where the stop does
nearly everything. It still isn't enough: the signal exits are
mostly small losses (breakouts that fall back to the middle).

## Verdict: loser, with the batch's familiar HYPE-only green leg

Same shape as every breakout system in this batch: BTC and ETH lose
by 13–25%, HYPE prints +19.4% (PF 1.18, the best HYPE leg among the
losers). Combined -$1,839 on 639 trades. The volatility adjustment
doesn't fix the core problem — on 1h bars, closes outside a 1.5xATR
band are usually the end of the move, not the start. Nothing here
approaches a live gate.

## Mechanism

SMA(20) +/- 1.5xATR(14) breakout, midline exit, 2xATR stop, 3xATR
chandelier trail, 120-bar max hold. All params fixed a priori; no
optimization.

Source: ATR bands / volatility channel (Wilder ATR; Murphy,
Technical Analysis of the Financial Markets).

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
