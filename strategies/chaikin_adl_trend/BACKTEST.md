# Chaikin ADL Trend — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), full cached range, read directly with pandas (no network).
BTC/ETH: 5,335 bars, 2026-03-14 22:00 UTC → 2026-10-22 23:00 UTC.
HYPE: 5,333 bars, 2026-03-15 00:00 UTC → 2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=70 bars.

## Results (shipped config: ADL cross vs SMA(10) + close vs SMA(50)
filter, opposite-cross exit, 1.5xATR stop, 2xATR chandelier trail,
72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 528 | 25.4% | -$6,372 | -63.7% | -5.10 | -64.4% | -$12.07 | 0.57 | $4,882 |
| ETH | 538 | 26.8% | -$6,754 | -67.6% | -6.06 | -67.7% | -$12.55 | 0.52 | $3,659 |
| HYPE | 446 | 32.7% | -$3,358 | -33.7% | -2.15 | -34.8% | -$7.53 | 0.78 | $2,525 |
| **Combined** | **1,512** | **28.0%** | **-$16,483** | — | — | — | — | — | **$11,066** |

Side split: BTC 274 long / 254 short (longs -$3,643, shorts
-$2,729); ETH 270 long / 268 short (longs -$3,234, shorts
-$3,520); HYPE 227 long / 219 short (longs -$1,022, shorts
-$2,335). Both sides lose on every coin.

## Verdict: a loser — the trend filter does not rescue the cross

Combined -$16,483 across 1,512 trades, 28.0% win rate, every leg
deeply red (PF 0.52–0.78). This is not a fee story: gross PnL
before fees is -$5,417, so the signals themselves lose — fees
($11,066) roughly triple the damage but do not cause it.

The mechanics point the way to why. The ADL is a cumulative
series, so its SMA(10) hugs it closely; the cross fires on small
money-flow wiggles, and the SMA(50) filter passes most of them
(price spends long stretches on one side of its 50-bar average
in any sustained move). The result is a high-frequency whipsaw
machine — 446–538 trades per coin over ~7 months, roughly 2–3
round trips a day — with a 25–33% win rate and a tight
opposite-cross exit that realizes every flicker quickly.

Honest read: as specified this is not tradeable. If the idea is
revisited, it needs a much slower signal line (e.g., SMA(50) of
the ADL, or an ADL rate-of-change threshold so only large
money-flow shifts fire), a choppiness gate, or a daily-scale
ADL — and any of that must be validated on walk-forward data,
not this window (see CALIBRATION.md: no in-sample tuning was
performed).

## Mechanism

MFM = ((c − l) − (h − c)) / (h − l), 0 on zero-range bars;
MFV = MFM × v; ADL = cumsum(MFV); signal = SMA(ADL, 10).
Long: ADL crosses above SMA(10) & close > SMA(50). Short:
mirror. Exit: opposite ADL cross. 1.5xATR stop, 2xATR chandelier
trail, 72-bar max hold. All params fixed a priori; no optimization.

Source: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:accumulation_distribution_line

## Limitations

- Single 7-month crypto window; all three legs deeply negative.
- Loses before fees as well as after — not a cost problem.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
