# CVD Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.
**Signal counts (per coin, full window):** BTC 161 long / 144 short
entries; ETH 141 / 126; HYPE 120 / 138 — every gate fires on every coin.

## Results (shipped config: EMA(CVD,20) slope turns positive/negative
for 2 bars + close vs EMA(50), exit on slope reversal, 2xATR stop,
3xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 303 | 29.7% | -$3,071 | -30.7% | -2.53 | -34.2% | -$10.14 | 0.71 |
| ETH | 265 | 29.1% | -$2,355 | -23.7% | -2.13 | -30.2% | -$8.89 | 0.74 |
| HYPE | 257 | 31.9% | -$1,262 | -12.6% | -0.93 | -20.1% | -$4.91 | 0.87 |
| **Combined** | **825** | **30.2%** | **-$6,688** | — | — | — | -$8.11 | — |

## Verdict: a loser on all three coins, HYPE least bad

Combined -$6,688 across 825 trades, and no leg is green: BTC -30.7%,
ETH -23.7%, HYPE -12.6%. The pattern is consistent — win rates stuck
at 29–32% with profit factors of 0.71–0.87, so the average loss beats
the average win on every coin. Two things plausibly drive it:

- The close-location proxy is a weak stand-in for true bid/ask CVD:
  on 1h bars the close's position in the range is a noisy classifier
  of aggressive flow, so the EMA(CVD,20) slope turns on noise as
  often as on real flow.
- The slope-reversal exit is hair-trigger: one negative-slope bar
  exits a long, so winners are cut before the 3xATR trail can work
  while the 2xATR stop still takes its full bite on losers.

Fees ($6,334 combined) are nearly as large as the net loss — at 825
trades the strategy pays almost a dollar in fees for every dollar it
loses. HYPE is the least-bad leg (PF 0.87, Sharpe -0.93), but
least-bad is not a signal. Ship as documented, paper-only.

## Mechanism

Close-location proxy: buy_vol=v×(c−l)/(h−l), sell_vol=v−buy_vol,
delta=buy_vol−sell_vol, CVD=cumsum(delta). Long when the EMA(CVD,20)
slope turns positive (rising 2 consecutive bars) with close above
EMA(50); short on the mirror image. Exit when the CVD slope reverses.
2xATR hard stop, 3xATR chandelier trail, 150-bar max hold.

Source: Cumulative Volume Delta (CVD) —
https://www.quantvps.com/blog/cumulative-volume-delta

## Limitations

- Close-location proxy ≠ true bid/ask CVD; tick-level data would give
  a different (possibly better, possibly worse) series.
- CVD level is anchor-dependent (never resets in-window); only the
  slope is traded, by design.
- Fast slope-reversal exits cut winners early; win rates 29–32%.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped EMA length on this window (see CALIBRATION.md).
