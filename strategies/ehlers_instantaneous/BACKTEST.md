# Ehlers Instantaneous Trendline — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), full cached range, read directly with pandas (no network).
BTC/ETH: 5,335 bars, 2026-03-14 22:00 UTC → 2026-10-22 23:00 UTC.
HYPE: 5,333 bars, 2026-03-15 00:00 UTC → 2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: close cross vs Instantaneous
Trendline alpha=0.07, opposite-cross exit, 1.5xATR stop, 2xATR
chandelier trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 781 | 24.2% | -$8,264 | -81.8% | -6.82 | -83.1% | -$10.58 | 0.55 | $5,345 |
| ETH | 830 | 22.5% | -$7,277 | -72.8% | -4.98 | -75.2% | -$8.77 | 0.65 | $5,051 |
| HYPE | 837 | 24.0% | -$6,541 | -65.5% | -4.62 | -66.6% | -$7.81 | 0.69 | $3,361 |
| **Combined** | **2,448** | **23.6%** | **-$22,082** | — | — | — | — | — | **$13,758** |

Side split: BTC 391 long / 390 short (longs -$4,579, shorts
-$3,686); ETH 415 long / 415 short (longs -$4,350, shorts
-$2,927); HYPE 419 long / 418 short (longs -$2,803, shorts
-$3,738). Both sides lose on every coin.

## Verdict: a heavy loser — low lag cuts both ways

Combined -$22,082 across 2,448 trades, 23.6% win rate, every leg
deeply red (PF 0.55–0.69, Sharpe −4.6 to −6.8). This is not a fee
story: gross PnL before fees is -$8,324, so the signals
themselves lose — fees ($13,758) deepen but do not cause the
loss.

The mechanics explain it, and they are the mirror image of the
sales pitch. Low lag means the IT hugs price closely, so the
close crosses it constantly: 781–837 trades per coin over
~7 months, roughly 3–4 round trips a day, at a 22–24% win rate.
The filter that "responds quickly to genuine trend changes"
also responds quickly to every chop flicker, and the
opposite-cross exit realizes each flicker within a few bars
while cutting winners before they run. Low lag bought speed
and paid for it in whipsaw — the classic smoother's dilemma,
with no free lunch on this window.

Honest read: as specified this is not tradeable. The low-lag
cross thesis is falsified on 1h crypto bars here. If the idea
is revisited, it needs the part of Ehlers' setup this spec
omits — the trigger line (2·IT − IT[2]) or a cycle filter so
crosses only fire with the dominant cycle — or a slower alpha,
and any of that must be validated on walk-forward data, not
this window (see CALIBRATION.md: no in-sample tuning was
performed).

## Mechanism

IT[i] = (alpha − alpha²/4)·P[i] + 0.5·alpha²·P[i−1]
− (alpha − 0.75·alpha²)·P[i−2] + 2·(1−alpha)·IT[i−1]
− (1−alpha)²·IT[i−2], alpha = 0.07, P = close, seeded with
price. Long: close crosses above IT. Short: mirror. Exit:
opposite cross. 1.5xATR stop, 2xATR chandelier trail, 72-bar
max hold. All params fixed a priori; no optimization.

Source: https://www.fmz.com/lang/en/strategy/436000

## Limitations

- Single 7-month crypto window; all three legs deeply negative.
- Loses before fees as well as after — not a cost problem.
- Close-input variant; the (h+l)/2 variant was not tested.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
