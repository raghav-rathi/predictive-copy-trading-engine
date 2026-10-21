# Elder Force Index — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:25 UTC
(ms `[1773446400000, 1792589132324)`): 5,296 bars BTC/ETH, 5,294 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: fi = (c − c.shift(1)) * v, entry timer fi2 =
EMA(fi,2), trend gauge fi13 = EMA(fi,13); long when fi13 > 0 and fi2
crosses below zero, short on the mirror, exits when fi13 crosses zero,
2xATR stop, 3xATR trail, 100-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 363 | 27.0% | -$4,003 | -39.24% | -2.76 | -44.71% | -$11.03 | 0.67 |
| ETH | 358 | 29.3% | -$2,936 | -28.60% | -1.75 | -37.77% | -$8.20 | 0.76 |
| HYPE | 330 | 30.0% | -$1,284 | -12.28% | -0.77 | -23.26% | -$3.89 | 0.89 |
| **Combined** | **1,051** | **28.7%** | **-$8,224** | — | — | — | -$7.82 | — |

## Verdict: clear loser — negative on every coin with a 1,051-trade sample

This one is decisive. The pullback-timing idea churns: fi2 crossing zero
is a hyperactive trigger on 1h bars, firing ~330–360 times per coin over
7 months, with a 27–30% win rate that never covers the trade costs.
Combined -$8,224 on a $10k start.

- **BTC is the disaster** (-$4,003, MaxDD **-44.71%**): the fi13 trend
  gauge spent the window's chop whipsawing around zero, so the "pullback"
  was really just volatility — the strategy bought dips that kept
  dipping. Nearly half the account died on this leg alone.
- **ETH is bad the same way** (-$2,936, MaxDD -37.77%): same trigger,
  same chop, same outcome.
- **HYPE is the "best" leg and still loses** (-$1,284, PF 0.89): the
  least-bad read in a uniformly negative sweep is not a silver lining.
- The 2xATR stop did not save anything: the exit rule (fi13 crossing
  zero) is as laggy as the entry is twitchy, and max-hold + trail
  entries bled out in trendless stretches.
- Unlike the divergence strategy, sample size is not the problem here —
  1,051 trades is enough to say the fi2-zero-cross trigger has no edge
  on 1h crypto perps in this regime.

## Calibration note

Shipped the specified trend EMA of 13. A 9/13/21 trend-length sweep is
in CALIBRATION.md: every setting is negative on every coin; 21 is the
least-bad (combined -$8,750 vs -$8,224 for 13 — no setting fixes it).
The trend length was fixed a priori — no in-sample adoption, and
nothing here suggests a different length would rescue the trigger.

## Mechanism

Force Index (Elder, 1993): fi = (close − prior close) * volume — the
force behind a move, weighting price change by how much volume moved
it. Two EMAs: fi2 = EMA(fi,2) is the entry timer, fi13 = EMA(fi,13) is
the trend gauge. Long when fi13 > 0 (bulls in charge) **and** fi2
crosses below zero (the pullback — price falling on volume weak enough
to drag the 2-bar average negative); short on the mirror. Exit when
fi13 itself crosses zero — the balance of power flipped, so the
trend premise is gone. 2xATR hard stop (pullbacks need room), 3xATR
chandelier trail, 100-bar max hold.

Source: Force Index (Alexander Elder, Trading for a Living) —
https://www.luxalgo.com/library/concept/force-index/

## Limitations

- Single 7-month crypto window — but 1,051 trades is a real sample,
  and it says no.
- The fi2 zero-cross is too twitchy on 1h bars: noise-driven entries
  dominate; fees alone take a large share of every trade.
- fi13 as both entry filter and exit trigger whipsaws around zero in
  chop, which is where the MaxDD came from.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped trend length on this window (see
  CALIBRATION.md).
