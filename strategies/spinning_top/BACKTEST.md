# Spinning Top — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, local cache only
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), batch-45 frozen window ms
`[1773525600000, 1795525200000)` (2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC exclusive; last bar 13:00 UTC): 6,111 bars
BTC/ETH, 6,109 HYPE (HYPE's first bar is 2026-03-15 00:00 UTC).
Run with the pinned runner `scripts/run_pinned_backtest45.py`
(reads cache only, never hits the API, never extends the window).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start per coin. WARMUP=30 bars.

## Results (shipped config: spinning top = body ≤ 30% of range
with both wicks ≥ 30%, long at the prior 20-bar low, short at
the prior 20-bar high, exit on the opposite signal, 2xATR
stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 97 | 29.90% | -$1,518.79 | -15.19% | -1.41 | -22.38% | -$15.66 | 0.74 | $1,021.95 |
| ETH | 72 | 34.72% | -$788.83 | -7.89% | -0.76 | -8.90% | -$10.96 | 0.80 | $585.78 |
| HYPE | 123 | 30.08% | -$1,741.50 | -17.42% | -1.33 | -20.32% | -$14.16 | 0.74 | $533.55 |
| **Combined** | **292** | **31.16%** | **-$4,049.12** | — | — | — | **-$13.87** | — | **$2,141.28** |

Net % is the final-equity return (it includes the mark-to-market
of any position still open at the window end); Net $ is the sum
of closed-trade PnL.

## Verdict: loser on all three coins — indecision is not exhaustion

Negative everywhere: combined -$4,049.12 on 292 trades, win rate
31.16%, profit factor 0.74–0.80 on every coin, expectancy
-$10.96 to -$15.66 per trade. The spinning top fires
as designed, but a small body at a 20-bar extreme on 1h crypto
is usually a pause inside a continuing move, not its end: the
trade is counter-trend into momentum, and the 2xATR stop pays
for the lesson. ETH is least-bad (-$788.83, MaxDD only -8.90%)
and still firmly negative. The extra 10 days vs the Nov-14
refresh window changed nothing about the verdict — combined net
moved from -$3,680 to -$4,049.12, same sign on every coin.

## Calibration note

Shipped the specified swing_lookback=20. A 10/20/40 swing
sweep re-run on this same batch-45 window is in CALIBRATION.md:
every setting is negative on every coin except one single-coin
positive (ETH→10 at +$1,072.84) that does not survive the other
two coins; combined net spans -$2,425.66 (40) to -$4,049.12 (20),
all negative. The swing window is not the problem — the pattern
itself does not reverse 1h trends. The 20-bar config was
fixed before any backtest was run; no in-sample adoption.

## Mechanism

Steve Nison, "Japanese Candlestick Charting Techniques"
(spinning top): per bar, rng = h − l, body = |c − o|,
upper_wick = h − max(o, c), lower_wick = min(o, c) − l.
Spinning top when body ≤ 0.30 × rng and both wicks ≥ 0.30 ×
rng (rng > 0, so a flat bar cannot qualify). Long when a
spinning top's low reaches the lowest low of the prior 20
bars (swing windows exclude the current bar, so the bar
cannot qualify itself); short mirror at the prior 20-bar
high. Exit on the opposite signal. 2xATR hard stop, 3xATR
chandelier trail, 60-bar max hold.

Source: Steve Nison, "Japanese Candlestick Charting
Techniques" (spinning top) —
https://www.candelacharts.com/patterns/spinning-top

## Audit note (batch 45 refresh)

No code changes were needed. Full re-audit on the batch-45
refresh: swing windows are shifted by one bar (the current
bar cannot qualify itself), candle anatomy uses only the
current bar's OHLC, signals are boolean with no NaN, and the
truncation test proves no lookahead (indicator/signal values
at bar j are identical whether computed on the full series or
on the series truncated at j). All 15 unit tests pass.

## Limitations

- Single 8.5-month crypto window; 292 trades, all negative —
  the failure is consistent, not a sample-size artefact.
- Counter-trend by construction: fading a 20-bar extreme on
  1h bars fights momentum, and the pattern has no confirmation
  (no next-bar follow-through required).
- A single wide spinning top can break both swing extremes at
  once and fire both a long and a short on the same bar; the
  harness takes the long (entries are checked long-first),
  which is an arbitrary tie-break, not a rule.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped swing lookback on this window.
