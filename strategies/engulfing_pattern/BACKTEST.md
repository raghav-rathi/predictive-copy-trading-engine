# Engulfing Pattern Reversal — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to 2026-03-14 → 2026-10-23 (`[1773446400000,
1792713599000)`; actual data starts 2026-03-14 22:00 UTC for
BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,330 bars BTC/ETH, 5,328
HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, both directions. WARMUP=60 bars.

## Results

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 469 | 27.7% | -$6,692 | -66.9% | -5.57 | -68.8% | -$14.27 | 0.54 |
| ETH | 455 | 28.4% | -$5,254 | -52.5% | -3.35 | -56.2% | -$11.55 | 0.66 |
| HYPE | 401 | 36.2% | -$1,485 | -15.0% | -0.68 | -24.1% | -$3.70 | 0.91 |
| **Combined** | **1,325** | **~30.5%** | **-$13,431** | — | — | — | -$10.14 | — |

Fees: BTC $3,976, ETH $3,529, HYPE $2,449 ($9,954 combined).

## Verdict: loser on all three coins — report it as such

This is not a "fee-bound marginal"; it is a structurally negative
strategy on 1h crypto:

- **Every leg is red**, with profit factors of 0.54–0.91 — the
  gross edge is negative *before* costs, so this is not a fee
  problem. BTC's Sharpe of -5.57 and -68.8% max drawdown on a
  $10k start is a blowup, not a wobble.
- **The EMA(20) "trend filter" does no real work.** A bullish
  engulfing is, by construction, a bar that pops up through its
  own short moving average — gating on close > EMA(20) on the
  engulfing bar's close mostly admits the same bars the raw
  pattern would have. The pattern fires 400–470 times per coin
  over 7 months: that frequency is the tell. A genuine
  trend-aligned reversal setup would be an order of magnitude
  rarer.
- **The canon's missing piece is location.** The source stresses
  that engulfings are trend- *and* location-dependent — swing
  structure, support/resistance, prior extremes. This build has
  the trend half (a same-timeframe EMA) and none of the location
  half, and the result says a 20-bar EMA is not a substitute for
  structure.

No parameter rescue: with combined expectancy at -$10.14/trade,
tuning the EMA length would be optimizing noise. The honest next
step is structural (multi-timeframe swing location) on
walk-forward data — see CALIBRATION.md.

## Mechanism

Bullish engulfing: green body fully covers the prior red body
(`c > o`, `c.shift(1) < o.shift(1)`, `c >= o.shift(1)`,
`o <= c.shift(1)`); bearish mirror. Long when bullish_eng and
close > EMA(20); short when bearish_eng and close < EMA(20);
exit on the opposite engulfing. 1.5xATR stop, 2xATR chandelier
trail, 48-bar max hold, acted on the closed candle.

Source:
https://halleytech.substack.com/p/reversal-candlestick-patterns

## Limitations

- Single 7-month crypto window; the strategy loses in all three
  coins, which is consistent but still one regime.
- Entries assume next-bar-open execution vs the idealized close
  of the engulfing bar.
- Funding unmodeled; perps funding would add a further drag on
  the longer-held trades.
- Never tune the shipped parameters on this window.
