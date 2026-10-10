# NR7 — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: NR7 narrowest-range-7 breakout of the NR7 bar's high/low, reverse-break exits, 1.5xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 368 | 24.7% | -$5,701 | -57.0% | -3.44 | -59.0% | -$15.49 | 0.65 |
| ETH | 351 | 27.6% | -$3,398 | -33.6% | -1.49 | -41.1% | -$9.68 | 0.79 |
| HYPE | 367 | 28.9% | -$5,496 | -55.0% | -4.06 | -55.0% | -$14.97 | 0.67 |
| **Combined** | **1,086** | **27.1%** | **-$14,595** | — | — | — | -$13.43 | — |

## Verdict: LOSER

Decisively negative on all three coins. The failure mode is structural, not
bad luck: 1,086 trades (~1 trade every 4.7 bars) means the NR7 setup on 1h
crypto bars flags compression constantly — crypto's jagged range profile
throws a "narrowest of 7" bar on nearly every consolidation wiggle, and the
break of that bar's high/low is noise, not expansion. Win rate 24.7-28.9%
with a 1.5xATR stop: the break fakes out, reverses, and the reverse-break
exit (which doubles as the stop-loss side) churns the account. Fees
($8.4k combined) compound the bleed, but profit factor 0.65-0.79 says the
gross edge is absent even before costs.

## Calibration note

Shipped exactly the specified parameters (7-bar window, close-break of the
NR7 bar's high/low, reverse exits, 1.5xATR stop, 24-bar max hold) — no
in-run parameter sweep; a two-variant robustness sweep ran separately and
is recorded in CALIBRATION.md. What I verified instead: `is_nr7` flags
exactly the hand-built narrowest bar and nothing else (unit tests), entries
fire only on prior-bar-NR7 + close break (never on non-NR7 breakouts, never
both sides), and indicators are lookahead-free by truncation test. What
didn't survive contact with data: the premise itself. Crabel's NR7 is a
daily-bar pattern where a true 7-bar range contraction is a rare,
meaningful compression; ported to 1h crypto, the pattern loses its rarity
and with it its meaning — the signal fires on ordinary chop and the
1.5xATR stop is just wide enough to bleed fees before giving up.

## Mechanism

Bar range = h - l; is_nr7[i] = range[i] == min(range[i-6..i]). On bar i,
if bar i-1 was NR7: long_entry = close[i] > high[i-1],
short_entry = close[i] < low[i-1] (first break wins; a single close can't
break both). Exits reverse on the opposite break; 1.5xATR stop and 24-bar
max hold handle the rest.

Source: NR7 breakout (Toby Crabel) — strategyvisualizer —
https://github.com/timcodes/strategyvisualizer/blob/HEAD/strategy-library/038-nr7-breakout.md

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized breakout entry; Crabel enters
  intraday at the break, so the 1h-close-confirm adds lag he doesn't pay.
- Daily-bar variant not tested; the daily pattern may be the real one.
