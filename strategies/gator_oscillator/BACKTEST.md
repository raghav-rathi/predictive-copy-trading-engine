# Gator Oscillator States — Backtest

**Data:** local cache CSVs (`data/candles/BTC_1h.csv`,
`ETH_1h.csv`, `HYPE_1h.csv`), columns t,o,h,l,c,v, t in ms; fully
offline, no API calls. Sliced to the batch window constants
`START_MS=1773446400000`, `END_MS=1792627199000`
(ms `[1773446400000, 1792627199000)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,301 bars
BTC/ETH, 5,299 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=40 bars. `run_backtest` with `use_funding=False`.

## Results (shipped config: 13/8/5 SMMA lengths, 8/5/3 displacements;
long on awakes->eats flip with bull fan, short with bear fan; exit on
sleeps or fan flip; 2xATR stop, 3xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 338 | 40.2% | -$2,911 | -28.8% | -2.50 | -29.4% | -$8.61 | 0.720 |
| ETH | 358 | 36.3% | -$2,997 | -30.0% | -2.42 | -32.0% | -$8.37 | 0.733 |
| HYPE | 329 | 41.3% | -$1,630 | -16.3% | -1.31 | -18.8% | -$4.95 | 0.853 |
| **Combined** | **1,025** | **39.1%** | **-$7,538** | — | — | — | **-$7.35** | — |

## Verdict: an honest loser on all three coins

The Gator Oscillator states strategy fails cleanly in this window.
All three coins are red, all three profit factors sit well under 0.9,
and all three Sharpe ratios are worse than -1.3. Combined -$7,538
across 1,025 trades with expectancy -$7.35 a trade — this is not a
fees story (fees are 25–110% of net loss across coins) but a signal
story: the awakes->eats flip with a fan filter fires 1,025 times in
seven months and the directional follow-through just is not there.

Notable failure mechanics:

- **BTC and ETH are deep losers** (-$2,911 and -$2,997, PF ~0.72–0.73,
  MaxDD −29 to −32%). On 1h crypto, the fan filter (lips>teeth>jaw)
  confirms trend late, after the balance lines have already
  displaced 8 bars forward; the eats expansion is often the end of
  the leg, not the start.
- **HYPE is the least-bad leg but still red** (-$1,630, PF 0.853,
  Sharpe −1.31). Unlike momentum strategies in this window it does
  not catch HYPE's trend legs — the Gator sleeps through the middle
  of moves and wakes at the tops.
- 1,025 trades in one regime is a large sample for a per-strategy
  call: the combined -$7.35 expectancy is well-estimated, and the
  uniform red across coins means there is no "coin the strategy
  works on" story to hide behind.

This ships as an honest loser. Do not run the shipped config live;
do not retune it on this window.

## Calibration note

The standard 13/8/5 lengths and 8/5/3 displacements were fixed a
priori (Bill Williams' canonical values) — adopted before any backtest
was run, not because of the results. A jaw-length sweep in {8, 13, 21}
with ratio-scaled teeth/lips and shifts is in CALIBRATION.md: every
setting is negative on every coin, and jaw=13 is the least-bad
combined — an in-sample observation, not a justification for the
shipped config.

## Mechanism

SMMA balance lines on median price: jaw=SMMA(13) displaced 8 bars,
teeth=SMMA(8) displaced 5 bars, lips=SMMA(5) displaced 3 bars
(displacements use past data only). Gator histograms: upper =
|jaw−teeth| above zero, lower = −|teeth−lips| below zero; bars green
when |value| rises vs the prior bar. Long on the awakes→eats flip
(both histograms flip green) with lips>teeth>jaw fan; short with
lips<teeth<jaw fan. Exits when the Gator sleeps (both histograms red)
or the fan order flips against the position. 2xATR hard stop, 3xATR
chandelier trail, 150-bar max hold.

Sources: Gator Oscillator (Bill Williams) —
https://www.ifcmfa.com/en/ntx-indicators/gator-oscillator; Alligator
indicator — https://www.luxalgo.com/blog/alligator-indicator/

## Limitations

- Single 7-month crypto window; uniformly negative, so the loser
  verdict is the robust part.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped lengths on this window (see CALIBRATION.md).
