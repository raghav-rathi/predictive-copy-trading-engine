# Volume Profile Value-Area Fade — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH (cache starts
2026-03-14 02:00 UTC), 5,269 HYPE (HYPE history starts 2026-03-15
00:00 UTC). Last bar 2026-10-20 12:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=200 bars.

## Results (shipped config: rolling 168-bar composite profile, 24 bins,
POC = max-volume bin, value area expanded to ≥ 70% of window volume,
long on failed breakdown below VAL (reclaim), short on failed breakout
above VAH, 2xATR stop, 3xATR target, 120-bar max hold, no signal exits)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 95 | 40.0% | -$1,023 | -10.4% | -1.15 | -14.2% | -$10.77 | 0.83 |
| ETH | 79 | 40.5% | -$601 | -6.0% | -0.67 | -15.5% | -$7.61 | 0.87 |
| HYPE | 80 | 36.2% | -$1,345 | -13.6% | -1.52 | -16.3% | -$16.82 | 0.74 |
| **Combined** | **254** | **39.0%** | **-$2,969** | — | — | — | -$11.69 | 0.81 |

## Verdict: loser — the failed-auction fade doesn't rotate on 1h crypto

254 trades, negative on all three coins (PF 0.74–0.87, expectancy
−$8 to −$17/trade). The 3xATR target as a "VAL→VAH rotation proxy" is
the flaw: on 1h crypto bars, a reclaim of VAL is as often a
dead-cat bounce into the next leg down as a genuine rotation, and the
2xATR stop is wide enough to turn those into full −$ losses while the
3xATR target rarely fills (win rates stuck near 40% with PF < 0.9 say
the winners aren't fat enough). The 168-bar profile itself is fine —
POC/VAH/VAL are honest — but the edge it maps is an intraday auction
concept; at 1h resolution the "failed auction" is usually just the
start of acceptance at a new price. Best of the three losers, which
says nothing good. Fees ($1,907 combined) are material here — the
book's gross edge is roughly zero before costs, and costs make it
negative.

## Calibration note

Shipped the specified 70% value-area coverage. A 60/70/80% sweep is in
CALIBRATION.md: all settings lose on all coins; 80% is least negative
in-sample (combined −$1,558) and 60% next (−$2,401) vs shipped −$2,969 —
but every variant is red, so adopting either would be in-sample
selection. Keep 70% as specified. The coverage knob moves the edges
but does not change the premise's failure.

## Mechanism

Rolling 168-bar composite volume profile in 24 equal price bins
spanning the window's [min low, max high]; each bar's volume spread
uniformly across the bins its [low, high] range touches (causal — only
bars ≤ i). POC = max-volume bin; value area expands outward from the
POC, each step adding the adjacent bin with the most volume, until ≥
70% of window volume is captured (VAH/VAL = outer edges). Long when
the prior close dipped below VAL and the current close reclaims it
(failed breakdown); short symmetric on failed breakouts above VAH
(VAL/VAH taken from the prior bar's profile, so the level is known
before the entry bar closes). No signal exits — 2xATR stop, 3xATR
target (rotation proxy), 120-bar max hold.

Source: Volume profile POC/VAH/VAL (markettrace.ai) —
https://markettrace.ai/blog/volume-profile-trading

## Limitations

- Single 7-month crypto window; 254 trades, all negative.
- 3xATR target is a proxy, not the actual VAH — rotations that reach
  VAH but not 3xATR (or vice versa) are mismodeled by construction.
- The composite profile recomputes 168×24 bins per bar (vectorized,
  ~seconds per coin) — fine for research, heavy for production.
- Value-area auction theory is an intraday concept; 1h bars smear the
  auction structure it assumes.
- Funding unmodeled; next-bar-open execution vs idealized entry.
