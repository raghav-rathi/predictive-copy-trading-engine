# Elder Ray — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Bull Power = H−EMA(13), Bear Power = L−EMA(13);
long when EMA rises and negative Bear Power turns up; short on the
mirror; exit when power crosses zero against the trade; 2xATR stop,
3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 241 | 25.7% | −$4,073 | −40.7% | −3.85 | −45.8% | −$16.90 | 0.53 |
| ETH | 234 | 30.3% | −$1,817 | −18.2% | −1.21 | −25.1% | −$7.76 | 0.82 |
| HYPE | 213 | 28.6% | +$543 | +5.4% | +0.51 | −20.4% | +$2.55 | 1.05 |
| **Combined** | **688** | **28.2%** | **−$5,347** | — | — | — | −$7.77 | — |

## Verdict: LOSER (weak mixed — HYPE barely positive)

−$5,347 combined. Elder's exhaustion-with-trend entry is elegant on
daily equities; on 1h crypto the "Bear Power turning up" fires on
every minor bounce inside downtrends, and the rising-EMA requirement
doesn't filter them because 13-bar EMA whipsaws too. BTC bleeds
−40.7% at PF 0.53. HYPE's +5.4% (Sharpe 0.51) is the same
trend-friendliness story as the rest of the batch, not an Elder edge.
Not a rescue candidate as built.

## Calibration note

Indicators verified: Bull/Bear Power match H−EMA/L−EMA exactly;
constructed-setup test confirms entries require rising EMA + negative
turning-up Bear Power; flat-market test confirms no spurious entries;
truncation test proves lookahead-freedom. Mechanism quirk: the
turn-detection (rising after not-rising) is a single-bar pattern on a
noisy series — most "turns" are noise, not exhaustion. Revisit path:
smooth Bear Power with a 3-bar average before turn detection, and
require the EMA slope over 5+ bars, not 1.
