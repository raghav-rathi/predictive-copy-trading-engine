# RSI MA Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), full cached range, read directly with pandas (no network).
BTC/ETH: 5,335 bars, 2026-03-14 22:00 UTC → 2026-10-22 23:00 UTC.
HYPE: 5,333 bars, 2026-03-15 00:00 UTC → 2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=40 bars.

## Results (shipped config: Wilder RSI(14) cross vs SMA(RSI, 14),
opposite-cross exit, 1.5xATR stop, 2xATR chandelier trail,
72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 928 | 23.8% | -$8,711 | -87.1% | -7.87 | -88.2% | -$9.39 | 0.55 | $5,759 |
| ETH | 906 | 25.1% | -$6,377 | -63.8% | -3.66 | -66.0% | -$7.04 | 0.74 | $6,377 |
| HYPE | 910 | 26.3% | -$7,658 | -76.7% | -6.27 | -76.9% | -$8.42 | 0.64 | $3,195 |
| **Combined** | **2,744** | **25.0%** | **-$22,746** | — | — | — | — | — | **$15,331** |

Side split: BTC 464 long / 464 short (longs -$5,363, shorts
-$3,347); ETH 453 long / 453 short (longs -$3,768, shorts
-$2,609); HYPE 455 long / 455 short (longs -$2,943, shorts
-$4,715). Both sides lose on every coin; the near-perfect
long/short symmetry is structural (an RSI cross up is always
followed by a cross down, and the harness takes them in turn).

## Verdict: a heavy loser — the RSI cross is a whipsaw machine

Combined -$22,746 across 2,744 trades, 25.0% win rate, every leg
deeply red (PF 0.55–0.74, Sharpe −3.7 to −7.9). This is not a fee
story: gross PnL before fees is -$7,415, so the signals
themselves lose — fees ($15,331) roughly triple the damage but
do not cause it.

The mechanics explain the scale. RSI hugs its own 14-bar average
closely, so the cross fires constantly: 906–928 trades per coin
over ~7 months, roughly 4 round trips a day, at a 24–26% win
rate. Each whipsaw pays the ~0.11% round-trip cost and, worse,
the opposite-cross exit guarantees the loss is realized within
a few bars while winners are cut by the same exit before they
can run — the system is structurally short patience.

Honest read: as specified this is not tradeable. The cross-only
thesis is falsified on this window. If the idea is revisited, it
needs a level gate (only take crosses out of overbought /
oversold zones), a trend filter, or a much slower signal line —
and any of that must be validated on walk-forward data, not
this window (see CALIBRATION.md: no in-sample tuning was
performed).

## Mechanism

Wilder RSI(14) vs SMA(RSI, 14). Long: RSI crosses above its
average. Short: mirror. Exit: opposite cross. 1.5xATR stop,
2xATR chandelier trail, 72-bar max hold. All params fixed a
priori; no optimization.

Source: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:relative_strength_index

## Limitations

- Single 7-month crypto window; all three legs deeply negative.
- Loses before fees as well as after — not a cost problem.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
