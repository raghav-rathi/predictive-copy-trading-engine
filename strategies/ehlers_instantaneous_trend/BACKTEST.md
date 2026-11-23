# Ehlers Instantaneous Trendline — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC/ETH 6,064 bars, HYPE 6,062 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin, long/short. WARMUP=30 bars.

## Results (shipped config: alpha = 0.07, price-vs-line +
line-slope entries, cross-back or line-turn exits; 2xATR
harness backstop; 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 736 | 22.4% | -$7,026 | -70.0% | -4.97 | -71.8% | -$9.55 | 0.61 |
| ETH | 782 | 20.3% | -$6,808 | -67.9% | -4.45 | -70.0% | -$8.71 | 0.62 |
| HYPE | 783 | 26.4% | -$2,579 | -25.2% | -1.18 | -33.1% | -$3.29 | 0.89 |
| **Combined** | **2,301** | **23.1%** | **-$16,412** | — | — | — | **-$7.13** | — |

Fees: BTC $4,607, ETH $3,929, HYPE $3,516 (total $12,052).

Exit reasons (BTC): 614 signal exits, 122 stops. Sides roughly
balanced (BTC 365 long / 371 short).

## Verdict: loser — the trendline hugs price and whipsaws

This is a clear, well-sampled loss: 2,301 trades across three
coins, win rate 20–26%, profit factor 0.61–0.89 on every coin,
Sharpe deeply negative everywhere. Price crosses a
near-zero-lag trendline every ~8 bars per coin, so the system
is almost always in a position, paying 0.055% per side on
every round trip while catching no trend long enough to pay
for the churn.

- Fees alone ($12,052) are 73% of the combined loss — but the
  gross edge is negative even before costs (profit factor well
  under 1.0 on all three coins), so this is not a
  "fees killed a winner" story. Removing costs would still
  leave a loser.
- The win rate near 20% with a 2xATR stop says the typical
  trade is entered on a wiggle and exited almost immediately
  on the next wiggle — the line-turn exit fires before any
  move develops.
- HYPE is the "least bad" coin (PF 0.89, win rate 26.4%) and
  still loses 25% of equity. No coin, no side, and no exit
  reason shows a pocket of edge.

Stated plainly: do not trade this as specified on 1h crypto.
The Instantaneous Trendline is a sound near-zero-lag filter,
but alpha = 0.07 unscaled makes it far too fast for hourly
bars — it tracks noise, not trend. Slowing alpha down would
be a different strategy and would need its own validation —
it is not adopted here.

## Mechanism

LONG when price is above the Instantaneous Trendline and the
line is rising; SHORT on the mirror; entries transition-only;
exit when price crosses back through the line or the line
turns against the position (opposite transition flips); 2xATR
harness backstop; 168-bar max hold. All params fixed a priori
from the Ehlers spec; no optimization.

Source: John Ehlers, Rocket Science for Traders (2001),
Instantaneous Trendline chapter
(https://www.mesasoftware.com/papers/).

## Limitations

- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The combined net $ sums three separate $10k accounts; the
  combined net % is therefore not reported.
- Never tune the shipped parameters on this window — least of
  all alpha, which directly controls how many trades fire.
