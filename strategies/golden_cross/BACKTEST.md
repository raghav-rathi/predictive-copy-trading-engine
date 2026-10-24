# Golden Cross / Death Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 2026-03-14 22:00 UTC →
2026-10-22 23:00 UTC (5,335 bars each), HYPE 2026-03-15 00:00 UTC
→ 2026-10-22 23:00 UTC (5,333 bars). 95 trades across the three
coins.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2.0xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=250 bars.

## Results (shipped config: SMA(50)/SMA(200) cross, long on Golden
Cross, short on Death Cross, exit on the opposite cross,
2.0xATR stop, 3.0xATR chandelier trail, 240-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 29 | 34.5% | -$540 | -5.4% | -0.85 | -10.6% | -$18.63 | 0.67 |
| ETH | 37 | 21.6% | -$1,486 | -14.9% | -2.79 | -15.8% | -$40.16 | 0.39 |
| HYPE | 29 | 41.4% | +$560 | +5.6% | +0.89 | -5.6% | +$19.31 | 1.40 |
| **Combined** | **95** | — | **-$1,466** | — | — | — | — | — |

Fees: BTC $321, ETH $315, HYPE $154 (total $790).
Long/short split: BTC longs +$10 / shorts -$550; ETH longs
-$503 / shorts -$982; HYPE longs +$763 / shorts -$203.
Exit reasons: 93 stop, 2 signal, 0 max-hold.

## Verdict: a thin, mostly red system — lag did not buy quality

Combined -$1,466 across only 95 trades is a small loss, but the
shape of it is damning, not reassuring. 93 of 95 trades exit on
the stop — the opposite-cross exit that is supposed to be the
whole trade almost never fires, because the 3.0xATR trail (or
the 2.0xATR stop) gets there first on a 10-day holding window.
So the strategy as traded is not "ride the regime until the
cross reverses"; it is "enter late on a lagging cross, then
exit on a wide trailing stop," and the entry's lateness means
the move is usually half over by the time the cross confirms —
there is not enough trend left to survive a 2xATR adverse
excursion.

ETH is the worst leg (21.6% win rate, PF 0.39): Death Cross
shorts into a window with strong upside drift, and Golden
Cross longs that trigger after ETH has already run. HYPE's
+$560 (PF 1.40, Sharpe +0.89) is the only green leg, but 29
trades cannot carry a system verdict — and a single green leg
among three is exactly what multiple comparisons produces.

Honest read: as specified this is not tradeable on 1h bars.
The classic 50/200 cross is a daily-chart signal for a reason:
compressing it to 1h bars keeps the lag but loses the regime
persistence that makes the daily version work. If the idea is
revisited, it belongs on daily bars (outside this 1h harness)
or with a trend-persistence filter — and any of that must be
validated on walk-forward data, not this window (see
CALIBRATION.md: no in-sample tuning was performed).

## Mechanism

SMA(50) vs SMA(200) of close. Long: SMA50 crosses above SMA200.
Short: SMA50 crosses below SMA200. Exit: opposite cross.
2.0xATR stop, 3.0xATR chandelier trail, 240-bar max hold. All
params fixed a priori; no optimization.

Sources: https://www.investopedia.com/terms/g/goldencross.asp

## Limitations

- Single ~7-month crypto window; 95 trades is a thin sample —
  but the exit-reason skew (93/95 stop) is a structural finding,
  not a sampling artifact.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
