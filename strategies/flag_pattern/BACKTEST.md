# Flag Pattern Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: >=3xATR pole in <=12 bars with stall,
5–15 bar consolidation <=1.5xATR and <=60% retrace, breakout entry,
reclaim exit, 1.5xATR stop, 2xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 37 | 24.3% | -$1,064 | -10.6% | -2.14 | -13.0% | -$28.77 | 0.47 |
| ETH | 22 | 13.6% | -$980 | -9.8% | -2.57 | -10.6% | -$44.56 | 0.29 |
| HYPE | 9 | 22.2% | +$545 | +5.5% | +1.74 | -3.0% | +$60.51 | 2.74 |
| **Combined** | **68** | — | **-$1,500** | — | — | — | -$22.05 | — |

Fees: BTC $445, ETH $217, HYPE $61 (total $723).
Exits: 46 stop / 22 signal — the tight 1.5xATR stop does most of
the killing, which fits a fast pattern with a tight stop, but the
win rates (13.6–24.3%) say the breakouts themselves are usually
false.

## Verdict: loser, thin

-$1,500 on 68 trades. BTC and ETH lose by ~10% each with the
batch's worst win rates (ETH 13.6%, PF 0.29 — the single worst leg
in the batch by profit factor). HYPE's +$545 on 9 trades is noise
with a flattering PF. The flag detector works as specified (it
finds real poles and consolidations — the unit tests prove the
mechanics), but at 1h granularity the breakout after a flag is
usually the last gasp of the pole's move, not a continuation. Nothing
here approaches a live gate.

## Mechanism

>=3xATR pole in <=12 bars with stall, 5–15 bar consolidation
<=1.5xATR and <=60% retrace, breakout entry, reclaim/opposite-flag
exit, 1.5xATR stop, 2xATR trail, 72-bar max hold. All params fixed
a priori; no optimization.

Source: flag pattern (Bulkowski, Encyclopedia of Chart Patterns).

## Limitations

- 68 trades total; HYPE's 9 trades say nothing.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
