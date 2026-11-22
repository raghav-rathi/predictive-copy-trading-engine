# Morales & Kacher Buyable Gap-Up — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC
(BTC/ETH 6,040 bars, HYPE 6,038 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=1,250 bars.

## Results (shipped config: gap ≥ 0.75×ATR(40) on ≥ 1.5× the
1,200-bar average volume in an uptrend; gap-bar low stop;
240-bar SMA exit; 2xATR harness backstop; 240-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 3 | 33.3% | +$540 | +5.4% | +1.47 | -3.0% | +$180.00 | 2.96 |
| ETH | 3 | 33.3% | +$546 | +5.5% | +1.47 | -3.1% | +$181.95 | 2.96 |
| HYPE | 4 | 25.0% | +$231 | +2.3% | +0.65 | -2.9% | +$57.72 | 1.91 |
| **Combined** | **10** | **30.0%** | **+$1,317** | — | — | — | **+$131.67** | — |

Fees: BTC $23, ETH $16, HYPE $16 (total $55).

## Verdict: inconclusive — 10 trades cannot validate a method

As flagged in the README, crypto has no true overnight gap, so
qualifying 1h gaps (open ≥ 0.75×ATR(40) above the prior close)
were expected to be rare. They were: 10 trades across three
coins in eight months, ~1 per coin per 10 weeks. The combined
+$1,317 with a +$131.67 expectancy looks like a winner until
you count the trades: 10. Three wins out of ten, and the
per-coin Sharpe figures (+1.47 on 3 trades) are meaningless at
this sample size — a single trade flipping sign moves every
number in the table.

- The positive sign on all three coins is mildly encouraging
  (a broken method would be expected to lose on at least one),
  but 3/3/4 trades per coin is not evidence; it is a hint at
  most.
- The expectancy (+$131.67/trade) is driven by a small number of
  gap-and-run moves that the 240-bar SMA exit let ride — the
  mechanism working as designed on the few occasions it fired.
- The flip side of the rarity: the strategy was flat for ~98% of
  the window. Even if the edge were real, the opportunity rate
  on 1h crypto is too low to matter without loosening the gap
  threshold — which would be tuning on this window, so we do not
  do it here.

Stated plainly: this backtest is inconclusive. The adaptation
works mechanically (gaps are detected, the gap-low stop and
240-bar exit fire as designed, unit-tested), but 10 trades
proves nothing about the BGU thesis on crypto. A real verdict
would need a much longer window, more coins, or the daily
timeframe where overnight gaps actually exist.

## Mechanism

LONG on open ≥ 0.75×ATR(40) above prior close with volume ≥
1.5× the 1,200-bar average, price above SMA50 and SMA200;
signal-level stop is the gap bar's intraday low; exit also on a
close below SMA(240) (10-day equivalent, simplified — see
CALIBRATION.md); short mirror is builder-added. All params fixed
a priori; no optimization.

Source: MaxMarkets, "Morales and Kacher Buyable Gap-Up"
(Morales & Kacher, *In the Buy Zone*)
(https://maxmarkets.app/learn/strategies/morales_kacher_bgu).

## Limitations

- 10 trades total: no statistic here is significant; do not
  quote the +$1,317 or the per-coin Sharpe figures as an edge.
- No true overnight gap in 24/7 crypto — the 1h gap adaptation
  is much smaller/rarer than the equity original.
- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window — least of all
  the 0.75× gap threshold, which directly controls how many
  trades fire.
