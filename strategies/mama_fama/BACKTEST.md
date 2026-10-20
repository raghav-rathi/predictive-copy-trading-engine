# Ehlers MAMA/FAMA Cross — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH, 5,269 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(`use_funding=False`).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: fastLimit=0.5, slowLimit=0.05, period clamp
[6,50], long on MAMA crossing above FAMA with close > MAMA, short on
the mirror, exits on the opposite cross, 2xATR stop, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 568 | 23.8% | -$5,409 | -54.0% | -3.28 | -61.6% | -$9.52 | 0.69 |
| ETH | 574 | 25.6% | -$5,141 | -51.4% | -2.88 | -61.4% | -$8.96 | 0.69 |
| HYPE | 518 | 30.5% | -$1,359 | -13.2% | -0.55 | -20.8% | -$2.62 | 0.93 |
| **Combined** | **1660** | **26.5%** | **-$11,909** | — | — | — | -$7.17 | — |

## Verdict: loser — the adaptive cross whipsaws on 1h crypto

Every coin loses, and the sample is anything but thin (1,660 trades).
The MAMA/FAMA cross fires far too often on 1h structure: with
fastLimit=0.5 the MAMA hugs price closely, so every chop prints a
cross, the close>MAMA confirmation rarely filters it, and the trade
grinds into the 2xATR stop at a 24–31% win rate with profit factors of
0.69–0.93. BTC is the worst leg (-54.0%, Sharpe -3.28, max drawdown
-61.6%); HYPE is merely bad (-13.2%, PF 0.93). Combined -$11,909 with
$10,289 in fees — costs are roughly half the story (the gross edge is
negative before fees too). The adaptive-alpha machinery is elegant,
but on this window it adapts to noise, not signal. Honest read: this
parameterization of MAMA/FAMA does not work on 1h crypto.

## Calibration note

Shipped fastLimit=0.5 as specified. A 0.4/0.5/0.6 fastLimit sweep is in
CALIBRATION.md: 0.4 is the in-sample winner (HYPE turns +$1,920,
combined -$9,177) and 0.6 the worst (combined -$14,249). The shipped
0.5 was kept as specified — adopting 0.4 now would be pure in-sample
selection, and 0.4 still loses on BTC/ETH combined.

## Mechanism

Hilbert-transform discriminator per Ehlers' original code: median
price → 4-bar weighted smoother → detrender → quadrature pair (I1/Q1)
→ 90°-shifted pair (jI/jQ) → smoothed phasor (I2/Q2) → phase-advance
(Re/Im, each 0.2/0.8 smoothed). Dominant period =
360/atan(Im/Re), clamped to [0.67x, 1.5x] of the prior period and to
[6, 50] bars. alpha = fastLimit / (period[i-1]/period[i]), clamped to
[0.05, fastLimit]: opens up when the cycle shortens, tightens when it
lengthens. MAMA = alpha-weighted price, FAMA = half-alpha MAMA.
Long on MAMA crossing above FAMA with close > MAMA; short on the
mirror; exit on the opposite cross. 2xATR hard stop, 200-bar max hold.

Source: Ehlers MAMA (prorealcode.com, from Ehlers' original code) —
https://www.prorealcode.com/prorealtime-indicators/john-ehlers-mama-the-mother-of-adaptive-moving-average/

## Limitations

- Single 7-month crypto window; but 1,660 trades is a large sample —
  this is a real loss, not a thin-sample fluke.
- 1h timeframe only; MAMA's adaptive period may behave better on
  higher timeframes (not tested here).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- No cross-confirmation beyond the close>MAMA filter; the raw cross
  rate (~1 per 9 bars) is too high for a 2xATR stop to absorb.
- MAMA alpha clamps (fastLimit/slowLimit/period bounds) are Ehlers'
  defaults, not tuned to crypto volatility.
