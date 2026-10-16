# Schaff Trend Cycle — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(`use_funding=False`).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.
No trailing, no fixed target, no max hold — exits come from the opposing
STC cross or the hard stop.

## Results

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 29 | 13.8% | -$365 (-3.6%) | -0.34 | -18.7% | -$12.57 | 0.87 |
| ETH | 24 | 20.8% | -$175 (-1.7%) | -0.05 | -16.8% | -$7.29 | 0.91 |
| HYPE | 19 | 5.3% | -$1,669 (-12.9%) | -1.86 | -17.8% | -$87.84 | 0.04 |
| **Combined** | **72** | **13.9%** | **-$2,209 (-7.4%)** | — | — | -$30.68 | — |

## Verdict: LOSER — not a standalone edge, no rescue worth chasing

Negative net PnL on all three coins, negative expectancy on every book,
profit factors below 1.0 everywhere. The single long entry fired only ~20
times per coin per year — this is a sparse, slow signal being asked to work
on 1h bars, and it fails: win rates of 5–21% mean the turns it picks are
mostly premature against the prevailing move. Nothing in the parameter
neighborhood saves it: the mechanism itself is wrong for crypto 1h timeframes.

## Calibration note

The Schaff Trend Cycle was designed for forex spot FX, a market with much
higher mean reversion at the daily scale than crypto perps. On 1h crypto
bars it acts as a fade-the-movers oscillator — exactly the losing side of
crypto's tendency to trend through overbought/oversold bands. HYPE shows
the pathology in its purest form: a 5.3% win rate with a -12.9% net return
means shorts fired into a sustained uptrend and each one was carried away
by continuation, not exhaustion. STC's double smoothing (EMA23→EMA50→EMA10)
also adds meaningful lag: by the time the cross through 25/75 prints, the
reversal it claims to detect is usually a pullback inside an intact trend.
Entries are sparse (19–29 trades per coin over 7 months), so even if the
hit rate improved, there is no volume to monetize. Do not port to daily bars
expecting a miracle — the mean-reversion-to-trend mismatch is structural,
not a timeframe artifact.

## Mechanism

MACD(12,26) line stochastically normalized over a 50-bar min/max window
(0–100), double-smoothed via EMA(23) then EMA(50), then a final EMA(10),
clipped 0–100. Long on cross up through 25, short on cross down through 75;
opposing cross exits. All signals computed from STC formed at the current
bar's close (shifted by 1) — no lookahead. 2xATR hard stop.

Source: [Doug Schaff, Schaff Trend Cycle](https://www.forex.in.rs/trend-cycle/)

## Limitations

- Single 7-month window, choppy-to-bearish crypto regime; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs the idealized cross-at-close entry.
- The 25/75 bands are Schaff's original FX thresholds; no attempt was made
  to re-optimize them for crypto (and nothing about the results suggests it
  would rescue the mechanism).
