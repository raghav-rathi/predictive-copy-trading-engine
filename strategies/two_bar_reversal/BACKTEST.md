# Two-Bar Key Reversal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
window ms `[1773525600000, 1795525200000)` (2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC, exclusive): 6,111 bars BTC/ETH, 6,109 HYPE.
Last closed bar 2026-11-24 13:00 UTC on all three. Batch-45 pinned
window — the Nov-14 numbers this file previously carried are deleted,
not preserved alongside.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=5 bars.

## Results (shipped config: confirmation = close above/below the
pattern bar's high/low, exits on the opposite reversal, 2xATR stop,
3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 387 | 31.01% | -$5,281.93 | -52.81% | -4.01 | -54.20% | -$13.65 | 0.59 | $2,756.97 |
| ETH | 386 | 31.61% | -$2,311.94 | -23.12% | -1.11 | -42.15% | -$5.99 | 0.84 | $2,736.78 |
| HYPE | 402 | 35.07% | +$212.05 | +2.12% | 0.25 | -25.79% | +$0.53 | 1.01 | $1,971.04 |
| **Combined** | **1,175** | **32.60%** | **-$7,381.81** | — | — | — | **-$6.28** | — | **$7,464.79** |

## Verdict: loser overall — the reversal doesn't reverse

Negative combined: -$7,381.81 on 1,175 trades, win rate
**32.60%**. BTC is the worst of the three (Sharpe -4.01, MaxDD
-54.20% — the $10k book more than halved) and ETH is clearly
negative too. The pattern fires as designed (~390 trades per
coin) but the "reversal" is usually a one-bar pause inside a
trend that resumes, and the win rate is ~31–35% on both sides,
so there is no directional asymmetry to exploit either.

The one honest nuance: gross of fees the book is essentially
flat — BTC -$2,524.96 gross (negative even before costs), ETH
+$424.84, HYPE +$2,183.08; combined gross **+$82.96** on 1,175
trades. The pattern has ~zero edge before costs and $7,464.79 of
fees turn it into a loser. HYPE is the only positive coin,
+$212.05 on 402 trades with PF 1.01 and Sharpe 0.25 — noise-level,
not an edge, and it flipped positive only in the last 10 days of
the window (it was -$655 in the stale Nov-14 window). Either way
there is nothing to rescue by tuning: the calibration sweep (see
CALIBRATION.md) shows looser confirmation only multiplies the
trade count and the losses.

The 10 extra days vs the stale Nov-14 window (238 more bars, 35
more trades) added +$363.19 net, driven by HYPE — and the verdict
is unchanged: the loss is consistent across BTC/ETH, both sides,
and both windows.

## Calibration note

Shipped the specified confirmation="high". A high/close/none
sweep is in CALIBRATION.md: "close" is far worse on every coin
(combined -$25,304.50, 5,053 trades) and "none" is catastrophic
(combined -$28,533.94, 6,628 trades, near-total wipeout on BTC/ETH).
The confirmation bar is doing real work — it filters out most of
the noise — but even the strictest version has no edge. The
"high" config was fixed before any backtest was run; no in-sample
adoption.

## Mechanism

Larry Williams' 2-bar key reversal ("Long-Term Secrets to
Short-Term Trading"): a down bar that makes a lower low is
exhaustion; the next bar closing above that bar's high confirms
the turn. Long on the confirmation, short on the mirror. Exits on
the opposite reversal signal. 2xATR hard stop, 3xATR chandelier
trail, 60-bar max hold — a one-bar setup plus one confirmation
bar goes stale fast, so a position that has not played out in
~2.5 days is a drift, not the pattern.

Source: Larry Williams, "Long-Term Secrets to Short-Term Trading"
(classic key reversal — the Fake Out / Key Reversal entry:
"if yesterday closed lower than the previous day, buy at
yesterday's high").
http://www.solerinvestments.com/Online-Trading/Larry-Williams-Trading.htm
— Williams's own description of the technique. Note the shipped
implementation is a stricter variant: it requires the confirmation
bar to *close* above the pattern bar's high, where Williams's
original triggers on trading above it.

## Audit (batch 45 refresh)

No code changes were needed. Audit of indicators.py / signals.py /
risk.py found no lookahead (every comparison uses backward shifts
only; the truncation test passes), no NaN poisoning (all signal
columns are boolean after `fillna(False)`; the row-0 NaN in
`lower_low`/`higher_high` from the 1-bar shift is handled), and
the exit logic is the specified opposite-reversal exit. Parameters
unchanged from the original build. 14/14 unit tests pass.

## Limitations

- Single 8.5-month crypto window; 1,175 trades is a decent sample
  and the loss is consistent across BTC/ETH and both sides.
- 32.60% win rate with PF < 1 on BTC/ETH — the edge is ~zero gross
  overall, negative gross on BTC; no confirmation setting rescues
  it (see CALIBRATION.md).
- The 2-bar pattern has no trend or volatility context: it fires
  into strong trends as readily as at range extremes, and the
  stop exits show the trend usually wins.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped confirmation mode on this window.
