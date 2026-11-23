# Ehlers Fisher Transform Trend — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC/ETH 6,064 bars, HYPE 6,062 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin, long/short. WARMUP=30 bars.

## Results (shipped config: 10-bar Fisher, 0.5/0.5 smoothing,
0-cross entries, cross-back or two-bar-turn exits; 2xATR
harness backstop; 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 655 | 30.5% | -$6,752 | -67.6% | -6.23 | -68.7% | -$10.31 | 0.57 |
| ETH | 692 | 30.2% | -$4,638 | -46.4% | -2.88 | -47.2% | -$6.70 | 0.73 |
| HYPE | 623 | 38.7% | -$3,932 | -38.8% | -3.17 | -41.0% | -$6.31 | 0.72 |
| **Combined** | **1,970** | **33.0%** | **-$15,322** | — | — | — | **-$7.78** | — |

Fees: BTC $4,457, ETH $4,289, HYPE $2,268 (total $11,014).

Exit reasons (BTC): 559 signal exits, 96 stops. Sides roughly
balanced (BTC 327 long / 328 short).

## Verdict: loser — the 0-cross whipsaws on 1h crypto

This is a clear, well-sampled loss, not an inconclusive one:
1,970 trades across three coins, win rate 30–39%, profit
factor 0.57–0.73 on every coin, Sharpe deeply negative
everywhere. The Fisher 0-cross on 1h bars flips every ~9 bars
per coin, so the system is almost always in a position, paying
0.055% per side on every round trip while catching no trend
long enough to pay for the churn.

- Fees alone ($11,014) are 72% of the combined loss — but the
  gross edge is negative even before costs (profit factor well
  under 1.0 on all three coins), so this is not a
  "fees killed a winner" story. Removing costs would still
  leave a loser.
- The two-bar-turn exit does not save it: 85% of BTC exits are
  signal exits, and the win rate stays near 30% — the exits
  cut both directions about equally.
- HYPE is the "least bad" coin (PF 0.72, win rate 38.7%) and
  still loses 39% of equity. No coin, no side, and no exit
  reason shows a pocket of edge.

Stated plainly: do not trade this as specified on 1h crypto.
The Fisher Transform is a sound near-Gaussianization, but its
0-cross is a regime flip that fires far too often at hourly
resolution to be a trend entry. A longer normalization window
or a confirmation filter would be a different strategy and
would need its own validation — it is not adopted here.

## Mechanism

LONG on the smoothed Fisher Transform crossing above 0 from
below while rising; SHORT on the mirror cross below 0 while
falling; exit on a cross back through 0 (which flips the
position) or two consecutive bars turning against it; 2xATR
harness backstop; 120-bar max hold. All params fixed a priori
from the Ehlers spec; no optimization.

Source: John Ehlers, "The Fisher Transform"
(https://www.mesasoftware.com/papers/TheFisherTransform.pdf).

## Limitations

- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The combined net $ sums three separate $10k accounts; the
  combined net % is therefore not reported.
- Never tune the shipped parameters on this window — least of
  all the 10-bar window or the 0-cross rule, which directly
  control how many trades fire.
