# Parabolic SAR stop-and-reverse — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; stop-and-reverse holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 3xATR safety stop, 3x leverage cap, $10k start.
**Config:** Wilder SAR, AF 0.02 + 0.02 capped at 0.20; flip flips the position
(stop-and-reverse); 40-bar warmup.

## Results (shipped config: AF 0.02→0.20)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 418 | 35.6% | -$2,564 | -25.6% | -1.97 | -41.9% | -$6.13 | 0.80 |
| ETH | 397 | 34.5% | -$1,678 | -16.7% | -1.17 | -24.0% | -$4.23 | 0.87 |
| HYPE | 486 | 36.8% | +$312 | +3.1% | 0.35 | -12.1% | +$0.64 | 1.02 |
| **Combined** | **1301** | **35.7%** | **-$3,930** | — | — | — | -$3.02 | — |

## Verdict: LOSER (BTC/ETH decisively, HYPE a wash)

Dead on the two majors with negative Sharpe on both; HYPE squeaks +$312 with
profit factor 1.02 — gross positive, but fees ($1.58k on HYPE alone, $6.3k
combined) eat it. The stop-and-reverse structure generates huge churn
(1,301 trades on ~15k bars — a flip every ~12 hours): on 1h crypto the SAR
whipsaws constantly, and the wide 3xATR safety stop lets losers run while
fees grind. AF 0.02→0.20, built for 1978 commodity dailies, reacts too fast
for 1h crypto — confirmed by the calibration sweep, where the *slower*
variant (AF 0.01→0.10) cut churn 29%, left BTC near breakeven, and made
HYPE solidly positive. The shipped config is the wrong AF for this
timeframe; the mechanism only survives on the trending coin (HYPE).

## Calibration note

Shipped exactly the specified Wilder parameters (AF 0.02 + 0.02, cap 0.20)
— the 2-variant sweep is documented in CALIBRATION.md. The signal logic is
verified lookahead-free by the truncation unit test. The failure is
parametric (AF speed vs 1h noise), not structural — which is why the slow
variant recovers: fewer flips, more trend capture.

## Mechanism

Wilder's Parabolic SAR as a stop-and-reverse system: SAR trails the trend,
accelerating (AF +0.02 per new extreme, capped 0.20); when price pierces the
SAR (low < SAR while long), the old stop becomes the new entry — flip short
and vice versa. SAR is the trailing stop; a 3xATR hard stop exists as a
safety net only.

Source: Parabolic SAR (J. Welles Wilder Jr.) — Disfold glossary —
https://blog.disfold.com/glossary/parabolic-sar/

## Limitations

- Single 7-month crypto window, choppy on the majors; no daily-bar test.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized SAR-pierce entry.
- AF variants only: no ADX trend filter was tested (likely the real fix).
