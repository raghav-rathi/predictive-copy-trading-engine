# Three-Line Break Turnaround — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC
(ms `[1773446400000, 1792414800000)`): 5,247 bars BTC/ETH, 5,245 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: 3-line break on closes, long on the
−1→+1 turnaround flip, short on +1→−1, exits on the opposite flip,
2xATR stop, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 4 | 75.0% | +$319 | +3.2% | +0.77 | -3.5% | +$79.83 | 3.92 |
| ETH | 4 | 0.0% | -$417 | -4.2% | -2.98 | -4.2% | -$104.34 | 0.00 |
| HYPE | 2 | 50.0% | +$107 | +1.1% | +0.48 | -2.3% | +$53.63 | 2.03 |
| **Combined** | **10** | **40.0%** | **+$9** | — | — | — | +$0.90 | — |

## Verdict: no evaluable edge — the system under-trades at this timeframe

A faithful three-line break on 1h crypto is an extremely low-frequency
system: on BTC it printed only 7 completed lines in 7 months, and one
line ran 2,629 bars (~3.6 months) through the summer trend. Across all
three coins there are 10 signals total. You cannot judge a strategy on
10 trades — the per-coin Sharpe and profit-factor numbers (BTC PF
3.92, ETH PF 0.00) are pure small-sample noise. The technique is a
regime filter, not an hourly signal generator: in a persistent trend a
single line runs for months and a reversal needs a full 3-line-range
retracement, so it structurally misses everything except major
turnarounds. Combined +$9 with $63 in fees is a coin flip with extra
steps.

## Calibration note

Shipped the specified 3-line reference. A 2/3/4-line sweep is in
CALIBRATION.md: it barely moves anything (BTC net $319 → $287, ETH and
HYPE identical). The binding constraint is line-break frequency at the
1h timeframe, not the parameter — there is no sensitivity worth
chasing here.

## Mechanism

Three-line break chart on closes: each line runs from the previous
line's close; a new white line prints when the close exceeds the high
of the last 3 lines during a black (down) sequence, a new black line
when the close falls below the low of the last 3 lines during a white
sequence; otherwise the close extends the developing line. Reference
convention: the "last 3 lines" are the 2 most recent completed lines
plus the developing line (documented choice — the more responsive of
the standard formulations; the first 2 bars are seeded as one line per
bar). Long on the −1→+1 turnaround flip, short on +1→−1; exits on the
opposite flip. 2xATR hard stop, 60-bar max hold.

Source: Three-line break —
https://th.tradingview.com/support/solutions/43000502273/

## Limitations

- 10 trades across 3 coins: no statistical meaning to any metric here.
- Single 7-month window; the technique's natural habitat is daily+
  timeframes, not 1h.
- In a sustained trend one line can run for months — the system is
  structurally blind to everything but major turnarounds.
- The developing-line-in-reference convention is a documented choice;
  a 3-completed-line variant would be even slower.
- Funding unmodeled; next-bar-open execution vs idealized entry.
