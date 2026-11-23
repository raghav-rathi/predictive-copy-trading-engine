# Hull MA Trend — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC/ETH 6,064 bars, HYPE 6,062 bars — counts verified against
the cache; HYPE's first bar is one hour later).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=100 bars.

## Results (shipped config: HMA(16) trigger, HMA(64) trend filter;
exit on close through HMA(16) or HMA(16) turning; 2xATR harness
backstop; 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 883 | 26.8% | -$7,062 | -70.7% | -6.08 | -71.8% | -$8.00 | 0.61 |
| ETH | 870 | 27.8% | -$6,257 | -62.4% | -4.34 | -62.8% | -$7.19 | 0.64 |
| HYPE | 903 | 35.0% | -$4,010 | -40.0% | -2.66 | -42.6% | -$4.44 | 0.78 |
| **Combined** | **2,656** | **29.9%** | **-$17,329** | — | — | — | **-$6.52** | **0.68** |

Fees: BTC $6,079, ETH $4,689, HYPE $3,350 (total $14,118).

## Verdict: loser — HMA's speed is a whipsaw machine on 1h crypto

This is a clear, high-sample loss, not a borderline one: 2,656
trades, a 29.9% win rate, profit factor 0.68, and a loss on every
coin. The mechanism failed exactly where the README flagged it
would be vulnerable. HMA(16) turns on nearly every hourly
wiggle, so the average trade lasted 3.5 bars — the strategy
bought the top of each hourly noise swing and sold the bottom
of the next one. Exits were 89% signal-driven (2,389 of 2,656)
and only 11% stops; the 168-bar max hold never fired once, which
is itself the diagnosis: nothing ever got to hold.

- Fees are most of the damage: $14,118 of the $17,329 combined
  loss (81%) is fees and slippage. At ~880 trades per coin the
  strategy pays the 0.055%-per-side round-trip cost roughly once
  every 7 bars — no trend edge of this size can survive that.
- The win rate (26.8–35.0%) is far below what a trend system
  needs at this payoff: with profit factor 0.61–0.78 the average
  win does not cover the average loss even before costs.
- HYPE lost the least (-40.0% vs BTC -70.7%), consistent with
  HYPE trending more cleanly than BTC/ETH in this window, but
  "least bad" is still a loss.

Stated plainly: do not trade this. The Hull average does what
it promises — it halves lag — and on 1h crypto that is a
liability, not an edge. A slower trigger (or an exit that
requires the slow average to turn) might fix the whipsaw, but
that would be a different strategy tuned on this window, so it
is not attempted here.

## Mechanism

LONG when C > HMA(16) with HMA(16) rising and C > HMA(64);
SHORT on the mirror; exit on a close back through HMA(16) or
HMA(16) turning against the position; transition-only entries
via a position state machine. All params fixed a priori; no
optimization.

Source: Alan Hull, "Hull Moving Average" (2005)
(https://alanhull.com/hull-moving-average).

## Limitations

- Single 8-month crypto window (a strong downtrend regime for
  much of it); funding unmodeled; next-bar-open execution vs
  idealized entry.
- The loss is large enough that the sign is robust, but the
  magnitudes are window-specific — do not quote -$17,329 as a
  general expectation.
- Never tune the shipped parameters on this window — least of
  all the 16/64 lengths, which directly control the trade count.
