# 1-2-3 Trend Change (Sperandeo) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 → 2026-10-18 (5,224 bars BTC/ETH; 5,222 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop (point-2 proxy),
3x leverage cap, $10k start. WARMUP=210 bars.

**Window note:** the batch brief's literal filter `[1741910400000,
1760828400000]` maps to 2025-03-14 → 2025-10-18, which is empty (the
cache starts 2026-03-14). The comment's intent ("2026-03-14 →
2026-10-18") matches the full cache, so the full cached range was used.

## Results (shipped config: 5-bar fractal pivots, 200-bar lookback
trend lines, 1-2-3 completion entries, opposite pattern reverses,
1.5xATR stop / 3xATR target as point-2 and 2R proxies, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 40 | 30.0% | -$948 | -9.5% | -1.40 | -16.0% | -$23.71 | 0.68 |
| ETH | 32 | 40.6% | +$296 | +3.0% | +0.51 | -8.5% | +$9.26 | 1.14 |
| HYPE | 38 | 34.2% | -$121 | -1.2% | -0.11 | -9.7% | -$3.19 | 0.95 |
| **Combined** | **110** | **34.5%** | **-$773** | — | — | — | -$7.03 | — |

## Verdict: LOSER

Net -$773 on 110 trades, negative expectancy on two of three coins.
BTC is the clearest failure (-$948, Sharpe -1.40, profit factor 0.68):
on 1h crypto the "trend line" fit off fractal pivots is fragile — the
lowest-pivot anchor often sits far back, the line gets re-fit every bar,
and by the time the three-step pattern (break → retest → interim-low
break) completes, the move is mostly done; entries chase the tail of
the reversal and the 1.5xATR stop eats the whipsaw. ETH's small win
(+$296, 32 trades) reads as noise against BTC's decisive loss. The
pattern is selective (110 trades vs 214 for the EWMAC trend system over
the same window), but selectivity without edge just means fewer, still-
losing trades.

## Calibration note

Shipped exactly the specified parameters (5-bar pivots, 200-bar
lookback, 1.5xATR stop / 3xATR target, 72-bar max hold, WARMUP=210, plus
a 72-bar pattern-staleness timeout documented in signals.py). A wider
stop/target variant (2.0/4.0xATR) is reported in CALIBRATION.md — it
loses less but does not turn the strategy positive.

## Mechanism

Uptrend line: lowest 5-bar pivot low in the last 200 bars connected to
the highest later 5-bar pivot low such that no in-between low dips below
the line. Bearish 1-2-3: (1) close crosses below the line; (2) the first
5-bar pivot high after the break that fails to exceed the break-bar high
becomes point 2 (a higher high invalidates); (3) close below the interim
swing low (lowest low between points 1 and 2) → short entry. Bullish
mirrors it. The opposite 1-2-3 completion reverses the position. Pivots
are consumed only once confirmed (formation bar ≤ i−2), so there is no
lookahead.

Source: Victor Sperandeo, *Trader Vic: Methods of a Wall Street Master* —
https://roboforex.com/blog/education/trading-like-sperandeo-1-2-3-reversal-and-2b-pattern/

## Limitations

- Single 7-month crypto window; the pattern was designed for daily
  equities, untested here on slower bars.
- Stop/target are ATR proxies for "above point 2" and "2R" — the true
  pattern distances vary per setup.
- Funding unmodelled; next-bar-open execution vs idealized entry.
- 110 combined trades is a thin sample for a three-step pattern.
