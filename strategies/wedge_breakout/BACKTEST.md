# Wedge Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=100 bars.

## Results (shipped config: 5-bar zigzag, two-pivot trendlines,
80-bar span, breakout entry, reclaim exit, 2xATR stop, 2.5xATR
trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 170 | 20.6% | -$2,791 | -27.9% | -2.95 | -32.7% | -$16.41 | 0.61 |
| ETH | 179 | 22.9% | -$1,838 | -18.4% | -1.91 | -24.8% | -$10.27 | 0.73 |
| HYPE | 146 | 30.1% | +$1,455 | +14.6% | +1.42 | -10.8% | +$9.97 | 1.27 |
| **Combined** | **495** | — | **-$3,174** | — | — | — | -$6.41 | — |

Fees: BTC $1,730, ETH $1,359, HYPE $763 (total $3,852).
Exits: 254 stop / 240 signal / 1 max-hold — the most balanced exit
mix among the losing strategies, which makes the loss more
informative: the signal exits work about as often as the stop kills,
and neither side wins.

## Verdict: loser — the wedge's convergence is real geometry, not a
tradeable edge

-$3,174 on 495 trades, with BTC and ETH losing by 18–28% and HYPE
green again (+$1,455, PF 1.27). The wedge fires far more often than
the other chart patterns (495 vs 60–81 trades), because two-pivot
trendlines converge constantly on noisy 1h data — most "wedges" are
random-walk artifacts, not compression before a break. The win rates
(20.6–30.1%) are the batch's lowest among pattern strategies.
Nothing here approaches a live gate.

## Mechanism

5-bar zigzag pivots, two-pivot trendlines, 80-bar span, breakout
entry, reclaim/opposite-wedge exit, 2xATR stop, 2.5xATR trail,
96-bar max hold. All params fixed a priori; no optimization.

Source: rising / falling wedges (Bulkowski, Encyclopedia of Chart
Patterns).

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Trendlines through two pivots are noisy by construction; a
  regression fit would be stabler but would be a different strategy.
- Never tune the shipped parameters on this window.
