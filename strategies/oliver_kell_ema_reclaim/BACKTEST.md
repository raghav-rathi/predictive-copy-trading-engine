# Oliver Kell 20-EMA Reclaim — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: BTC/ETH 6,040 bars, HYPE 6,038 bars,
2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR(14) stop, 3x
leverage cap, $10k start, long/short. WARMUP=210 bars.

## Results (shipped config: cross back above the 20 EMA after a
5-19% pullback on quiet volume, above a rising 200 SMA with
rising 10/20 EMAs; exit on a close below the 20 EMA; 2xATR(14)
stop; 336-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| ETH | 8 | 25.0% | +$15 | +0.1% | +0.07 | -3.4% | +$1.82 | 1.09 |
| HYPE | 51 | 19.6% | -$169 | -1.7% | -0.34 | -4.9% | -$3.31 | 0.88 |
| **Combined** | **59** | **20.3%** | **-$154** | — | — | — | **-$2.62** | — |

Fees: BTC $0, ETH $48, HYPE $194 (total $241).

## Verdict: loser on the trades it took, and it never traded BTC

Combined -$154 on 59 trades is a small loss, not a blowout —
but the details are worse than the headline:

- **BTC: 0 trades in 8 months.** The gate set never fires on
  BTC. Diagnostic on the BTC window: 397 closes crossed back
  above the 20 EMA; 119 of those also passed the rising-200-SMA
  / rising-EMA trend filter; **0** of those also sat in the
  5–19% pullback band. The band is measured over trailing 20
  bars, so a qualifying pullback needs a 5%+ drop and a reclaim
  inside ~20 hours — on 1h BTC that essentially never happens.
  Kell's band is a daily-scale idea (a 5–19% pullback over
  weeks); compressed bar-for-bar onto 1h bars it starves the
  strategy. The short side is 0 trades for the same reason.
- **HYPE: 51 trades, 19.6% win, PF 0.88, -$169.** The setup
  fires on HYPE (a more volatile, trendier coin) and loses
  slowly: the 20-EMA exit cuts winners at the first close
  below the average while the 2xATR stop takes the full loss
  on failures. A 19.6% win rate with PF under 1.0 means the
  average win is not paying for the average loss.
- **ETH: 8 trades, +$15.** Noise — eight trades cannot
  support any conclusion.

Stated plainly: no edge demonstrated. The daily→1h period
mapping breaks the core pullback band on BTC, and where the
setup does fire (HYPE) it loses. The honest read is that this
is a daily-bar strategy run on the wrong timeframe; a fair test
would need daily bars (or a wider pullback lookback — which
would be a redesign, not a tuning tweak, and is out of scope
for this batch).

## Mechanism

Cross back above the 20 EMA after a 5–19% pullback to/below it
on quiet volume, gated by price above a rising 200 SMA with
rising 10/20 EMAs; mirror for shorts. Exit on a close below
the 20 EMA; 2xATR(14) stop approximates the source's 3% hard
stop; 336-bar max hold. All params fixed a priori; no
optimization. Deviations (3% stop → 2xATR, wedge pop not
formalized, daily → 1h mapping) are documented in
CALIBRATION.md.

Sources: Backtest Lab, "He Made 941% in One Year" (Oliver Kell)
(https://www.youtube.com/watch?v=WjcZaEJHlCE); rules also at
https://americancompound.substack.com/p/he-made-941-in-one-year-buying-pullbacks.

## Limitations

- BTC sample is empty; ETH sample is 8 trades; only HYPE has a
  usable sample and it loses.
- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window — in
  particular, do not widen the pullback band or lookback until
  this window looks good; that would be pure overfitting.
