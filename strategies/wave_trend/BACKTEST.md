# WaveTrend Oscillator — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to `[1773446400000, 1792713599000)` (2026-03-14 00:00
UTC → 2026-10-22 23:59 UTC; actual data starts 2026-03-14 22:00 UTC
for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,330 bars BTC/ETH,
5,328 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, longs + shorts. WARMUP=80 bars.

## Results (shipped config: canonical LazyBear formula n1=10/n2=21/
wt2 SMA(4), cross-in-zone entries ±53, extreme exits ±60,
1.5xATR stop, 2xATR chandelier trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 152 | 32.2% | -$2,922 | -29.2% | -2.88 | -33.0% | -$19.23 | 0.58 |
| ETH | 125 | 30.4% | -$1,499 | -15.0% | -1.35 | -30.1% | -$11.99 | 0.77 |
| HYPE | 153 | 32.7% | -$1,235 | -12.5% | -1.08 | -17.5% | -$8.07 | 0.83 |
| **Combined** | **430** | **31.9%** | **-$5,656** | — | — | — | -$13.15 | — |

Fees: BTC $1,824, ETH $1,176, HYPE $935 (total $3,935).

## Verdict: the classic oscillator loses everywhere on 1h crypto, and it is not a fee problem

This is an honest, unambiguous loser:

- **Negative on all three coins** with profit factors of 0.58 /
  0.77 / 0.83. Win rates sit at 30–33% and expectancy is negative
  by a full trade's worth of noise margin on every coin (-$19.23
  on BTC).
- **Not fee-bound:** strip every dollar of fees and slippage and
  the combined result is still roughly -$1,720. The entry logic
  itself loses — the oscillator's zone-cross signal on 1h crypto
  bars buys oversold bounces that keep falling and sells
  overbought strength that keeps running.
- **BTC is the worst by far** (Sharpe -2.88, -33% max DD): the
  ±60 extreme-exit never saves it because the 1.5xATR stop bleeds
  first, and the 72-bar max hold closes mean-reversion attempts
  that would have needed a week to work.

Why it fails here: LazyBear tuned the ±53/±60 lines on daily
equity/forex charts. On 1h crypto bars the WaveTrend's slower,
smoother tci spends long stretches pinned in the zones, so the
"cross from oversold" signal fires late into moves that are
already exhausting themselves, and the tight 1.5xATR stop
guillotines the entries before any reversion can arrive. A longer
max hold or wider stop might change the shape, but that is
parameter-fitting on this window — not what this file does.

## Mechanism

ap = (h+l+c)/3; esa = EMA(ap,10); d = EMA(|ap-esa|,10);
ci = (ap-esa)/(0.015·d) (ci=0 when d=0); wt1 = EMA(ci,21);
wt2 = SMA(wt1,4).
Long: crossed_above(wt1,wt2) & prior wt1 < -53; exit on
crossed_below(wt1,wt2) or wt1 > 60. Short: mirror (±53/∓60).
1.5xATR stop, 2xATR chandelier trail, 72-bar max hold.

Sources: https://www.fmz.com/lang/en/strategy/449714 —
https://usethinkscript.com/threads/wavetrend-oscillator-for-thinkorswim-lazybear.233/page-4

## Limitations

- Single 7-month crypto window; 430 trades.
- All three legs negative with PF < 1 — the signal loses gross
  of fees, not just net.
- 1h timescale only; the oscillator's zone lines were tuned for
  daily bars and were not rescaled here (deliberately — no
  in-sample tuning; see CALIBRATION.md).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped ±53/±60 on this window.
