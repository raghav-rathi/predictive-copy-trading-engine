# Accelerator Oscillator — Backtest

**Data:** local cache CSVs (`data/candles/{BTC,ETH,HYPE}_1h.csv`,
columns t,o,h,l,c,v; t in ms), fully offline, no API calls. Window ms
`[1773446400000, 1792627199000)`; actual bars after slicing: 5,301
BTC/ETH (2026-03-14 22:00 → 2026-10-21 13:00 UTC), 5,299 HYPE
(2026-03-15 00:00 → 2026-10-21 13:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=50 bars. Next-bar-open execution.

## Results (shipped config: fast=5, slow=34, signal=5 — Williams'
originals, fixed a priori; 2-bar with-trend / 3-bar counter-trend
entries, exits on the opposite entry condition or 2 bars of the
against color, 2xATR stop, 2.5xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1,054 | 29.7% | -$9,397 | -94.0% | -12.24 | -94.0% | -$8.92 | 0.38 |
| ETH | 1,073 | 30.3% | -$9,105 | -91.1% | -9.93 | -91.7% | -$8.49 | 0.45 |
| HYPE | 986 | 37.2% | -$6,942 | -69.4% | -5.81 | -70.9% | -$7.04 | 0.65 |
| **Combined** | **3,113** | **32.3%** | **-$25,444** | — | — | — | -$8.17 | — |

## Verdict: an unambiguous loser — Williams' color rules are a whipsaw machine on 1h crypto

Every leg is deeply negative, every metric is bad, and the sweep
(CALIBRATION.md) shows nothing rescues it. AC flips color almost every
few bars on the 1h timeframe, so the "2 green bars" entry is barely a
filter: ~1,000+ trades per coin in 7 months, a 29–37% win rate, and a
-$8 expectancy per trade. Two-thirds of exits are the color-flip
signal exit, not the stop — the strategy is constantly reversing
itself on noise and paying 0.055%/side for the privilege (fees alone:
$3,762 BTC, $3,447 ETH, $2,829 HYPE).

The uncomfortable truth for the thesis: Williams designed these rules
for discretionary, multi-timeframe trading where the trader filters
signals against trend context — the mechanical 2/3-bar count, without
that filter, is just a fast mean-reversion coin flip with a negative
edge. HYPE, the "easy" coin in this window for other strategies, still
loses -$6,942 with a -5.81 Sharpe. There is no coin here to hide
behind.

## Calibration note

Shipped (5, 34, 5) — Williams' original parameters — fixed A PRIORI
before any backtest was run. A slow=21/34/55 sweep is in
CALIBRATION.md: all nine settings lose between -$6,942 and -$9,397 per
coin. The slow length moves nothing; the rule set itself is the
problem, not the parameterization.

## Mechanism

med = (h+l)/2; ao = SMA(med,5) − SMA(med,34); ac = ao − SMA(ao,5).
Bar color = bar-to-bar change of ac (green if rising, red if
falling — color is the change, not the level). Long when AC>0 with 2
green bars or AC<0 with 3 green bars; short symmetric. Zero line alone
never signals. Exits on the opposite entry condition or 2 consecutive
bars of the against color. 2xATR stop, 2.5xATR trail, 120-bar max
hold.

Source: Accelerator Oscillator (Bill Williams, New Trading
Dimensions) —
https://www.gate.com/learn/articles/accelerator-oscillator-vs-awesome-oscillator

## Limitations

- Single 7-month crypto window; 3,113 trades but all in one regime.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Exit reasons: signal exits dominate (697/1054 BTC, 725/1073 ETH,
  706/986 HYPE) — the trail almost never binds before the color exit.
- Never tune parameters on this window to "fix" it (see
  CALIBRATION.md) — the sweep shows parameter changes do not change
  the sign.
