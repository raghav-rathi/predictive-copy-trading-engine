# ARMS Index (TRIN) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=20 bars.

## Results (shipped config: TRIN(10), long on a cross below 0.7 after
being above 1.0, short on a cross above 1.5 after being below 1.0,
exit on reversion into the 0.9–1.1 band, 1.5xATR stop, 2xATR target,
24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 458 | 41.7% | -$4,311 | -43.1% | -3.08 | -46.1% | -$9.41 | 0.76 | $5,279 |
| ETH | 451 | 39.9% | -$3,627 | -36.3% | -2.23 | -52.5% | -$8.04 | 0.76 | $3,516 |
| HYPE | 390 | 43.8% | -$3,303 | -33.2% | -2.48 | -36.3% | -$8.47 | 0.80 | $2,234 |
| **Combined** | **1,299** | **41.7%** | **-$11,241** | — | — | — | **-$8.65** | — | **$11,029** |

Signal gates fire constantly (long entries 306/310/243, short entries
263/275/243 for BTC/ETH/HYPE) — TRIN on 1h bars whipsaws through its
levels hundreds of times, so the strategy trades ~5 times a day and
pays $11,029 in fees to lose $11,241. ETH's -52.5% max drawdown is
the deepest of the four batch-37 strategies.

## Verdict: heavy loser — fee-bleed plus wrong-way washouts

Combined -$11,241 across 1,299 trades. The washout premise fails on
a single asset: a 10-bar TRIN below 0.7 on one coin's candles is not
a market panic flushing out, it is usually just a strong down-leg
gathering pace — buying it catches a falling knife, and the 24-bar
cap exits before any mean reversion arrives. Every coin loses
30%+; no coin, no metric is defensible.

## Calibration note

Shipped the specified 10-bar window. A 5 – 10 – 20 sweep is in
CALIBRATION.md: no setting is green on all three coins; the 20-bar
window is least bad combined (-$3,153) but still red on BTC and ETH.
The 10-bar window was fixed a priori — adopted before the sweep,
not because of it.

## Mechanism

TRIN = (up-bars / down-bars) / (up-volume / down-volume) over a
rolling 10-bar window, every component floored at 1. Long when TRIN
crosses below 0.7 after being above 1.0 in the prior 10 bars (panic
washout); short when it crosses above 1.5 after being below 1.0.
Exit when TRIN reverts into the 0.9–1.1 band. No trade if either
10-bar volume sum is 0. 1.5xATR stop, 2xATR target, 24-bar max hold.

Source: ARMS Index / TRIN (Richard Arms) —
https://investing.university/articles/arms-index-trin/

## Limitations

- Single-asset candle/volume proxy, not exchange-wide TRIN — the
  core caveat; the washout signal has no market-breadth content
  when computed on one coin.
- 1,299 trades at ~$8.49/trade in fees: the strategy is dominated
  by its own transaction costs even before the negative edge.
- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped window on this window (see CALIBRATION.md).
