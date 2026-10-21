# Woodies CCI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
window ms `[1773446400000, 1792590766516)` (2026-03-14 00:00 UTC →
2026-10-21 13:52:46 UTC, END computed at run time): 5,296 bars
BTC/ETH (first available bar 2026-03-14 22:00 UTC), 5,294 HYPE
(first available bar 2026-03-15 00:00 UTC); last closed bar
2026-10-21 13:00 UTC on all three.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: CCI(14) trend + CCI(6) turbo, 6-bar
zero-line trend qualifier, long on pullback into [0,50] with turbo
hooking back above zero, short mirror, exits on CCI(14) crossing the
zero line, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 82 | 20.7% | -$454 | -4.5% | -0.67 | -10.6% | -$5.54 | 0.84 |
| ETH | 75 | 21.3% | -$575 | -5.8% | -0.87 | -11.4% | -$7.67 | 0.78 |
| HYPE | 76 | 28.9% | -$356 | -3.6% | -0.51 | -10.2% | -$4.69 | 0.87 |
| **Combined** | **233** | **23.6%** | **-$1,385** | — | — | — | -$5.95 | — |

## Verdict: loser on all three coins — the pattern fires, the trend
doesn't follow

Negative everywhere: combined -$1,385 on 233 trades, win rate
**23.6%**, profit factor 0.78–0.87 on every coin. The Zero-Line
Reject premise does not pay on 1h crypto: the turbo hook through
zero fires as designed, but the "trend" that qualified on six bars
of +CCI has no persistence — entries bleed straight into the 2xATR
stop, and the zero-line exit closes whatever is left. The losses
are small per trade (MaxDD only -10% to -11%, the mildest
drawdowns in recent batches) but relentless: expectancy -$4.69 to
-$7.67 per trade on every coin.

The one honest nuance: gross of fees the book is +$481 (BTC +$468,
ETH +$9, HYPE +$4) — i.e. the pattern is approximately *zero-edge*
before costs, and $1,867 of fees turn it into a steady loser. There
is nothing to rescue here by tuning: the signal is a coin flip that
charges admission.

## Calibration note

Shipped the specified trend_bars=6. A 4/6/9 trend-qualifier sweep is
in CALIBRATION.md: every setting is negative on every coin; the
per-coin "best" reads are still losers (ETH→9 at -$320, BTC→6 at
-$454, HYPE→6 at -$356), and 9 bars is worst on BTC (-$905,
PF 0.67). The qualifier length is not the problem — six bars of
CCI>0 simply does not define a tradeable trend on this timeframe.
The 6-bar config was fixed before any backtest was run; no
in-sample adoption.

## Mechanism

Ken Wood's CCI system, mechanical Zero-Line Reject: typical price
(h+l+c)/3, CCI(n) = (tp − SMA(tp,n)) / (0.015 × mean|tp − SMA|).
CCI(14) is the trend line — which side of the zero line it holds,
and for how long, defines the tradeable direction. The fast CCI(6)
turbo is the trigger. Long when CCI(14) has held above zero for 6+
consecutive bars AND pulled back into [0,50] (tagging toward the
zero line without crossing it) while the turbo hooks back up through
zero; short mirror on the downside. Exits when CCI(14) itself
crosses the zero line — the premise is gone. 2xATR hard stop, 3xATR
chandelier trail, 60-bar max hold.

Source: Woodies CCI (Ken Wood) —
https://ftmo.com/fr/blog/woodies-cci-system/

## Limitations

- Single 7-month crypto window; 233 trades is a thin sample.
- 23.6% win rate with PF < 0.9 on all three coins — the edge is
  ~zero gross, negative net; no parameter rescues it (see
  CALIBRATION.md).
- The 6-bar zero-line qualifier is a weak trend definition on 1h
  bars; a real trend filter (ADX, structure) would be a different
  strategy, not a calibration.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped trend_bars on this window.
