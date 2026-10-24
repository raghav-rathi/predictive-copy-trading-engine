# Bollinger %B Band-Tag Reclaim — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 2026-03-14 22:00 UTC →
2026-10-22 23:00 UTC (5,335 bars each), HYPE 2026-03-15 00:00 UTC
→ 2026-10-22 23:00 UTC (5,333 bars). 741 trades across the three
coins.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=50 bars.

## Results (shipped config: BB(20, 2.0), long on %B cross above 0,
short on %B cross below 1, exit on the 0.5 cross, 1.5xATR stop,
2xATR chandelier trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 253 | 35.2% | -$4,691 | -44.1% | -3.61 | -47.9% | -$18.54 | 0.56 |
| ETH | 231 | 39.4% | -$479 | -4.8% | -0.18 | -14.9% | -$2.07 | 0.96 |
| HYPE | 257 | 35.0% | -$3,825 | -38.2% | -3.05 | -41.1% | -$14.88 | 0.65 |
| **Combined** | **741** | — | **-$8,995** | — | — | — | — | — |

Fees: BTC $2,677, ETH $2,354, HYPE $1,402 (total $6,433).
Long/short split: BTC longs -$2,577 / shorts -$2,113; ETH longs
-$1,209 / shorts +$731; HYPE longs -$391 / shorts -$3,434.
Exit reasons: 605 stop, 136 signal, 0 max-hold.

## Verdict: a loser on all three coins — the reclaim is not a filter

Combined -$8,995 across 741 trades, no green leg (best is ETH
at -$479, PF 0.96 — a coin flip after fees). The mechanism
diagnosis is in the exit reasons: 605 of 741 trades die on the
stop, only 136 reach the mid-band signal exit. The reclaim
fires, price flickers back inside the band, then re-reverses
through the 1.5xATR stop before ever reaching 0.5. In other
words, on 1h crypto bars a %B reclaim of the band edge is
usually just the band edge being noisy — the tag/reclaim
sequence happens several times inside a single trending move,
and each reclaim is a fresh opportunity to be stopped out.

The short side is the worst leg (HYPE shorts -$3,434): shorting
band tags in a window with strong upside drift fights the trend
on both entry and exit. BTC's -47.9% max drawdown on a 1%-risk
system is the number that kills it outright — the stop
clustering means losses arrive in correlated bursts, not as
independent 1% hits.

Honest read: as specified this is not tradeable. If the idea is
revisited, it needs a regime gate (trade tags only when a
higher-timeframe trend or range condition holds) or a much
wider stop — and any of that must be validated on walk-forward
data, not this window (see CALIBRATION.md: no in-sample tuning
was performed).

## Mechanism

BB(20, 2.0); %B = (close − lower) / (upper − lower), 0.5 on a
zero-width band. Long: %B crosses above 0. Short: %B crosses
below 1. Exit: 0.5 cross. 1.5xATR stop, 2xATR chandelier trail,
72-bar max hold. All params fixed a priori; no optimization.

Sources: https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands

## Limitations

- Single ~7-month crypto window; 741 trades is a solid sample
  for a reclaim system, and it rejects the idea.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
