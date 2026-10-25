# Classic Pivot Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=20 bars.

## Results (shipped config: prior-bar PP/R1/S1 breakout, PP exit,
1.5xATR stop, 2xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1,505 | 24.9% | -$9,674 | -96.7% | -13.32 | -96.7% | -$6.43 | 0.44 |
| ETH | 1,467 | 26.1% | -$9,209 | -92.1% | -9.91 | -92.6% | -$6.28 | 0.54 |
| HYPE | 1,504 | 29.8% | -$9,000 | -90.0% | -9.90 | -90.2% | -$5.98 | 0.53 |
| **Combined** | **4,476** | — | **-$27,883** | — | — | — | -$6.23 | — |

Fees: BTC $6,248, ETH $6,006, HYPE $3,625 (total $15,879).
Exits: 3,442 signal / 1,034 stop — the PP exit fires most of the
time, which is the tell: price breaks R1/S1, then immediately falls
back through PP. The system is a whipsaw machine by construction.

## Verdict: the batch's worst strategy — a structural failure, not a
tuning problem

-$27,883 across 4,476 trades, with equity drawdowns of 90–97% on
every coin. This is not a marginal loser: the strategy nearly wipes
out the account on all three coins independently. It loses before
fees too (BTC gross -$3,426 after removing $6,248 of fees), so
cheaper execution would not save it. The mechanism is the problem:
a "level" built from one bar's range breaks on almost every bar
(~1,500 trades per coin in 7 months — a trade every 3–4 bars), and
the PP exit then closes most of them for small losses. No parameter
tweak fixes a level with no memory; the fix would be a different
level (multi-bar or daily pivots), which is a different strategy.
Do not trade this. Do not tune this.

## Mechanism

Prior-bar PP/R1/S1 breakout, PP exit, 1.5xATR stop, 2xATR trail,
72-bar max hold. All params fixed a priori; no optimization.

Source: classic floor-trader pivot formula (PP/R1/S1 from
prior-period HLC).

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window — the failure is
  structural, and tuning it would be overfitting a broken premise.
