# Slow Stochastic — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range, no slicing: BTC 5,335 bars and ETH
5,335 bars from 2026-03-14 22:00 UTC, HYPE 5,333 bars from
2026-03-15 00:00 UTC, all to 2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=40 bars.

## Results (shipped config: %K(14)/%D(SMA 3) cross inside the
20/80 zones, opposite-cross exit, 1.5xATR stop, 2xATR chandelier
trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 296 | 28.4% | -$4,826 | -48.3% | -5.62 | -49.4% | -$16.30 | 0.44 |
| ETH | 260 | 35.4% | -$2,562 | -25.6% | -2.51 | -25.8% | -$9.85 | 0.68 |
| HYPE | 384 | 28.4% | -$4,797 | -48.0% | -5.61 | -51.1% | -$12.49 | 0.49 |
| **Combined** | **940** | **30.3%** | **-$12,184** | — | — | — | -$12.96 | — |

Fees: BTC $3,225, ETH $2,508, HYPE $1,767 (total $7,500).
Net % is the harness equity-curve return per leg; combined
net $ is the sum of per-leg trade PnL.

## Verdict: the worst of this batch — a loser on all three legs

Combined -$12,184 across 940 trades, 30.3% win rate, profit
factor 0.44–0.68 on every leg. BTC and HYPE both lose ~48% of
starting equity with Sharpe below -5.6. The zone filter does
not save it: a %K/%D cross inside the 20/80 zone on 1h crypto
bars is still mostly chop — the oscillator lives in the
extremes during trends (it pegs at 0 or 100 while price runs),
so "cross while oversold" fires repeatedly into a falling
market as each bounce attempt crosses and fails, and the
opposite-cross exit realizes each failure within a few bars.
The short side is no better in a 7-month net-uptrend window:
overbought crosses fire into strength that keeps running.

The deeper problem is the timeframe. Lane's stochastic was a
daily-chart tool for range-bound equities; on hourly crypto,
where ranges expand violently and trends persist for days,
the 14-bar window is too short to define a meaningful range
and the 3-bar %D is too fast to filter anything. The result
is a whipsaw machine that pays ~0.055% round-trip cost on
nearly every flicker — fees alone ($7,500) exceed half the
total loss.

Honest read: as specified this is not tradeable. If the idea
is revisited, it needs a regime gate (trade stochastic turns
only inside a proven range, e.g. ADX below a threshold) or a
longer window (daily bars, where Lane's tool was designed to
work) — and any of that must be validated on walk-forward
data, not this window (see CALIBRATION.md: no in-sample
tuning was performed).

## Mechanism

%K = 100*(c - lowest low 14)/(highest high 14 - lowest low
14) (zero range -> 50); %D = SMA(3) of %K. Long: %K crosses
above %D while %K < 20; short: mirror above 80. Exit:
opposite cross. 1.5xATR stop, 2xATR chandelier trail, 72-bar
max hold. All params fixed a priori; no optimization.

Sources: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:stochastic_oscillator

## Limitations

- Single 7-month crypto window; all three legs deeply negative.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
