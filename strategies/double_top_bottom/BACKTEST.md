# Double Top / Double Bottom — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=80 bars.

## Results (shipped config: 5-bar zigzag, 1.5% extreme tolerance,
neckline break, reclaim exit, 2xATR stop, 2.5xATR trail, 96-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 44 | 18.2% | -$1,207 | -12.1% | -2.36 | -17.5% | -$27.44 | 0.44 |
| ETH | 7 | 42.9% | +$292 | +2.9% | +0.96 | -3.8% | +$41.66 | 2.29 |
| HYPE | 13 | 15.4% | -$270 | -2.7% | -1.03 | -3.1% | -$20.78 | 0.45 |
| **Combined** | **64** | — | **-$1,186** | — | — | — | -$18.53 | — |

Fees: BTC $421, ETH $46, HYPE $56 (total $523).
Exits: 42 stop / 21 signal / 1 max-hold — two thirds of trades die
on the stop. The neckline break, like most 1h reversal entries, is
usually the continuation of the move that made the second extreme,
not its reversal.

## Verdict: loser, thin on two coins

-$1,186 on 64 trades, with BTC (-$1,207, 18.2% win, PF 0.44) doing
nearly all the damage. ETH (+$292) and HYPE (-$270) are 7 and 13
trades — noise. The pattern fires rarely enough (64 trades in 7
months across three coins) that the BTC leg is the only leg with
any weight, and it says the neckline break at 1h granularity is a
losing entry. Nothing here approaches a live gate.

## Mechanism

5-bar zigzag pivots, 1.5% extreme tolerance, neckline break entry,
reclaim/opposite-pattern exit, 2xATR stop, 2.5xATR trail, 96-bar max
hold. All params fixed a priori; no optimization.

Source: double top / double bottom (Bulkowski, Encyclopedia of
Chart Patterns).

## Limitations

- 64 trades total; ETH and HYPE legs are single-digit/low-teen
  samples — do not quote them as edges or failures.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
