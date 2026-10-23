# RSI(14) Swing-Pivot Divergence — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to the window 2026-03-14 00:00 UTC →
2026-10-22 23:59 UTC (ms `[1773446400000, 1792713599000)`; actual
data starts 2026-03-14 22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC
for HYPE): 5,330 bars BTC/ETH, 5,328 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, both directions. WARMUP=80 bars.

## Results (shipped config: RSI(14), confirmed 3/3 swing pivots,
regular + hidden divergences, entries on the confirmation bar of
the newly confirmed pivot pair, opposite-divergence exits,
1.5xATR stop, 2xATR chandelier trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 237 | 36.3% | -$2,823 | -28.2% | -1.80 | -38.0% | -$11.91 | 0.72 |
| ETH | 241 | 34.4% | +$1,435 | +14.3% | +0.91 | -25.1% | +$5.95 | 1.12 |
| HYPE | 210 | 35.2% | -$160 | +1.5%* | +0.22 | -16.2% | -$0.76 | 0.98 |
| **Combined** | **688** | — | **-$1,548** | — | — | — | **-$2.25** | — |

Fees: BTC $2,431, ETH $2,800, HYPE $1,317 (combined $6,548).

\* HYPE's Net % is mark-to-market: a long was still open at the
window's last bar (+$309 unrealized), so MTM equity reads +1.5%
while closed trades sum to -$160. Net $ is closed-trade PnL.

## Verdict: combined red — the classic ruleset does not survive mechanization on 3-bar fractals

- **BTC is a clear loser** (-$2,823, PF 0.72, Sharpe -1.80,
  expectancy -$11.91/trade, maxDD -38%). Fading 1h swing
  exhaustion on BTC just pays the trend.
- **ETH's green is fee-adjacent** (+$1,435 against $2,800 in fees;
  expectancy +$5.95 is ~2.4 trades from zero). Not an edge.
- **HYPE is flat** (-$160 closed, PF 0.98) — noise around zero.
- **Combined -$1,548 over 688 trades**, expectancy -$2.25/trade,
  win rates 34–36% across all three coins.

The failure mode is structural, not parametric: the textbook
divergence ruleset is a *discretionary* pattern read on significant
swings. Mechanized on every confirmed 3/3 fractal it fires ~1.3
signals/day per coin (270 entries/coin over the window) — most of
them minor RSI wiggles between forgettable pivots, not the major
momentum-exhaustion events the pattern is meant to capture.
Regular divergences in particular fade moves that, on 1h crypto,
more often continue. The 3-bar confirmation lag also means entries
land 3 bars after the pivot extreme, surrendering the best part of
the reversal to the lag.

Honest read: a losing system as shipped. The fix, if any, would be
selectivity — minimum pivot separation, minimum RSI swing
amplitude, or divergence only at higher-timeframe structure —
but that is a different strategy, to be built and validated
separately, never tuned on this window (see CALIBRATION.md).

## Mechanism

RSI(14) vs confirmed 3/3 swing pivots (pivot usable 3 bars after
its center; no lookahead). Regular bullish (price LL + RSI HL) and
hidden bullish (price HL + RSI LL) enter long; regular bearish
(price HH + RSI LH) and hidden bearish (price LH + RSI HH) enter
short — one signal per pivot pair, on the confirmation bar. Longs
exit on bearish-divergence confirmation, shorts on
bullish-divergence confirmation. 1.5xATR stop, 2xATR chandelier
trail, 96-bar max hold, both directions.

Sources: https://www.tradingsim.com/blog/divergence —
https://www.tradingview.com/scripts/search/rsi%20divergence/

## Limitations

- Single 7-month crypto window; 688 trades is a decent sample and
  the combined read is negative, not ambiguous.
- BTC leg strongly negative; ETH leg marginal with fees ≈ 2× net;
  HYPE leg flat.
- Entries fire on every 3-bar fractal divergence (~1.3/day/coin)
  — the pattern's selectivity is lost at this resolution.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
